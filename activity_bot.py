#!/usr/bin/env python3
"""
activity_bot.py — appends timestamps to heartbeat.txt and commits them.
Run directly or via GitHub Actions.
"""

import subprocess
import random
import time
import hashlib
from datetime import datetime, timezone

# Weighted daily target. Two is intentionally most common, zero is rare.
DAILY_COMMIT_WEIGHTS = {
    0: 0.06,
    1: 0.18,
    2: 0.44,
    3: 0.22,
    4: 0.10,
}

HEARTBEAT_PATH = "heartbeat.txt"


def rng_for_day(day_key):
    seed = hashlib.sha256(day_key.encode("utf-8")).hexdigest()
    return random.Random(int(seed[:16], 16))


def weighted_daily_target(day_key):
    rng = rng_for_day(day_key)
    pick = rng.random()
    cumulative = 0

    for count, weight in DAILY_COMMIT_WEIGHTS.items():
        cumulative += weight
        if pick <= cumulative:
            return count

    return 2


def count_today_entries(day_key):
    try:
        with open(HEARTBEAT_PATH, "r") as f:
            return sum(1 for line in f if line.startswith(day_key))
    except FileNotFoundError:
        return 0


def planned_commits_for_run(target, already_done, now):
    remaining = max(target - already_done, 0)
    if remaining == 0:
        return 0

    # Morning run handles roughly the first half; later/manual runs catch up.
    if now.hour < 15:
        return min(remaining, target // 2)

    return remaining


now = datetime.now(timezone.utc)
day_key = now.strftime("%Y-%m-%d")
target_commits = weighted_daily_target(day_key)
already_done = count_today_entries(day_key)
commits_this_run = planned_commits_for_run(target_commits, already_done, now)

if commits_this_run == 0:
    print(f"No activity commit needed today ({already_done}/{target_commits}).")
    raise SystemExit(0)

# Random delay: 0–20 minutes, to make commit times look natural.
delay_seconds = random.randint(0, 20 * 60)
time.sleep(delay_seconds)

# Commit messages pool — picked randomly for variety
messages = [
    "Update activity",
    "Routine update",
    "Keep it going",
    "Daily sync",
    "Heartbeat",
    "Maintenance update",
    "Regular check-in",
]

import os
git_email = "arnavgokhale12@users.noreply.github.com"
git_name = "arnavgokhale12"

# Override any environment variables set by the Actions runner
git_env = {
    **os.environ,
    "GIT_AUTHOR_NAME": git_name,
    "GIT_AUTHOR_EMAIL": git_email,
    "GIT_COMMITTER_NAME": git_name,
    "GIT_COMMITTER_EMAIL": git_email,
}

subprocess.run(["git", "config", "user.email", git_email], check=True)
subprocess.run(["git", "config", "user.name", git_name], check=True)

for index in range(commits_this_run):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(HEARTBEAT_PATH, "a") as f:
        f.write(f"{timestamp}\n")

    message = random.choice(messages)
    subprocess.run(["git", "add", HEARTBEAT_PATH], check=True)
    subprocess.run(
        ["git", "commit", "--author", f"{git_name} <{git_email}>", "-m", message],
        check=True,
        env=git_env,
    )

    if index < commits_this_run - 1:
        time.sleep(random.randint(3 * 60, 18 * 60))

print(f"Created {commits_this_run} activity commit(s) ({already_done + commits_this_run}/{target_commits} today).")
