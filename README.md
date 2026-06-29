# ChangeRadar GitHub Action

Flag **breaking changes in your dependencies** right in your CI — with links to what changed and how
to migrate. Free, runs on any push/PR or a weekly schedule.

## Use it
Add `.github/workflows/changeradar.yml` to your repo:

```yaml
name: ChangeRadar
on:
  pull_request:
  schedule: [{ cron: "0 13 * * 1" }]   # weekly Monday
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: kaicheng042008-sudo/changeradar-action@v1   # ← your published action repo
```

It scans `package.json` / `requirements.txt`, checks each dependency against ChangeRadar, and writes a
summary to the workflow run (tracked deps + any recent breaking changes + migration links).

## Publish (owner, one-time, free)
1. Create a public GitHub repo `changeradar-action`.
2. Put `action.yml` + `check.py` (this folder) at its root.
3. Tag a release `v1`. Now anyone can `uses: <you>/changeradar-action@v1`.

## Why it grows ChangeRadar
Every repo that adds it runs ChangeRadar in their CI and links back on every PR — in-workflow,
word-of-mouth distribution with zero ad spend. The free action is the top of the funnel to Pro.
