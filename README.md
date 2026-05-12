# ghrm — GitHub Activity Bot

Keeps your GitHub contribution calendar active by automatically committing a timestamp to `heartbeat.txt` once or twice a day.

## How it works

- **`activity_bot.py`** — chooses a weighted daily commit target from 0–4, with 2 most common and 0 rare. Each run appends timestamp entries to `heartbeat.txt`, commits them with randomly chosen messages, and sleeps random offsets so commits don't land at the exact same time each day.
- **`.github/workflows/activity.yml`** — GitHub Actions workflow that runs the script at ~9 AM and ~6 PM UTC daily.

## Toggling on/off

**To pause** (without deleting the workflow), open `.github/workflows/activity.yml` and change:

```yaml
if: true
```

to:

```yaml
if: false
```

Commit and push — the workflow will be skipped on every run until you change it back.

**To stop permanently**, delete `.github/workflows/activity.yml`.

**To trigger manually**, go to your repo on GitHub → Actions → "Activity Bot" → "Run workflow".

## Setup

1. Push this repo to GitHub (see commands below).
2. GitHub Actions uses the built-in `GITHUB_TOKEN` — no extra secrets needed.
3. Make sure Actions are enabled in your repo settings (Settings → Actions → Allow all actions).

```bash
git remote add origin https://github.com/<your-username>/ghrm.git
git push -u origin main
```
