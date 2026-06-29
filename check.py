#!/usr/bin/env python3
"""
ChangeRadar GitHub Action — scans a repo's dependencies, flags ones with recent breaking changes,
and links to migration details. Posts a job summary (+ PR-comment-ready markdown). stdlib only, $0.
Consumes the public API at https://changeradar.pages.dev/libs.json.
"""
import os, re, json, urllib.request

WS = os.environ.get("GITHUB_WORKSPACE", ".")
API = os.environ.get("CHANGERADAR_API", "https://changeradar.pages.dev/libs.json")

def norm(n):
    n = (n or "").lower().strip()
    return re.sub(r"^@[^/]+/", "", n)  # drop npm scope (@org/pkg -> pkg)

def read_deps():
    deps = set()
    pj = os.path.join(WS, "package.json")
    if os.path.exists(pj):
        try:
            j = json.load(open(pj, encoding="utf-8"))
            for k in ("dependencies", "devDependencies", "peerDependencies"):
                deps.update((j.get(k) or {}).keys())
        except Exception:
            pass
    for fn in ("requirements.txt", "requirements-dev.txt", "pyproject.toml"):
        p = os.path.join(WS, fn)
        if os.path.exists(p):
            for line in open(p, encoding="utf-8", errors="ignore"):
                m = re.match(r"^\s*['\"]?([A-Za-z0-9._-]+)", line)
                if m:
                    deps.add(m.group(1))
    return {norm(d) for d in deps if d}

def main():
    deps = read_deps()
    try:
        req = urllib.request.Request(API, headers={"User-Agent": "changeradar-action"})
        libs = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception as e:
        libs = {}
        print(f"ChangeRadar API fetch failed: {e}")

    def aliases(slug, repo):
        s = {slug, norm(repo)}
        for x in (slug, norm(repo)):
            if x.endswith(".js") or x.endswith(".py"):
                s.add(x[:-3])               # next.js -> next
            elif x.endswith("js") and len(x) > 3:
                s.add(x[:-2])               # nextjs -> next
        return {a for a in s if a}
    matched = {}
    for slug, info in libs.items():
        if deps & aliases(slug, info.get("repo", "")):
            matched[slug] = info
    breaking = {s: i for s, i in matched.items() if i.get("breaking")}

    L = ["## 🛰️ ChangeRadar — dependency breaking-change check\n"]
    if not matched:
        L.append("No tracked dependencies matched (ChangeRadar tracks 100+ popular libraries). "
                 "[Browse all →](https://changeradar.pages.dev)")
    else:
        L.append(f"Tracking **{len(matched)}** of your dependencies — **{len(breaking)}** shipped a "
                 f"recent breaking change.\n")
        if breaking:
            L.append("| Library | Latest | Heads-up |")
            L.append("|---|---|---|")
            for s, i in breaking.items():
                note = (i.get("lines") or ["breaking changes — see details"])[0]
                L.append(f"| [{i['repo']}]({i['url']}) | `{i.get('latest','')}` | {note} |")
        else:
            L.append("✅ No breaking changes detected in your tracked dependencies right now.")
        L.append("\n_Want **instant** alerts the moment a dependency breaks? "
                 "→ https://changeradar.pages.dev/pricing_")
    summary = "\n".join(L)

    sp = os.environ.get("GITHUB_STEP_SUMMARY")
    if sp:
        open(sp, "a", encoding="utf-8").write(summary + "\n")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        open(out, "a", encoding="utf-8").write(f"breaking_count={len(breaking)}\nmatched_count={len(matched)}\n")
    print(summary)

if __name__ == "__main__":
    main()
