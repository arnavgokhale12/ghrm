#!/usr/bin/env python3
"""
activity_bot.py — appends timestamps to heartbeat.txt and commits them.
Run directly or via GitHub Actions.
"""

import subprocess
import random
import time
import hashlib
from datetime import datetime, timedelta, timezone

# Weighted daily targets. Two is intentionally most common.
WEEKDAY_COMMIT_WEIGHTS = {
    0: 0.06,
    1: 0.16,
    2: 0.44,
    3: 0.24,
    4: 0.10,
}

WEEKEND_COMMIT_WEIGHTS = {
    0: 0.22,
    1: 0.38,
    2: 0.28,
    3: 0.09,
    4: 0.03,
}

# Rarely create a two-day break. This is deterministic per day so both
# scheduled runs agree on whether today is a break day.
BREAK_START_PROBABILITY = 0.025
MAX_COMMITS_PER_RUN = 2
HEARTBEAT_PATH = "heartbeat.txt"


def rng_for_day(day_key):
    seed = hashlib.sha256(day_key.encode("utf-8")).hexdigest()
    return random.Random(int(seed[:16], 16))


def is_break_start(day_key):
    rng = rng_for_day(day_key)
    return rng.random() < BREAK_START_PROBABILITY


def is_break_day(day):
    yesterday = day - timedelta(days=1)
    return is_break_start(day.isoformat()) or is_break_start(yesterday.isoformat())


def weighted_daily_target(day):
    if is_break_day(day):
        return 0

    day_key = day.isoformat()
    weights = WEEKEND_COMMIT_WEIGHTS if day.weekday() >= 5 else WEEKDAY_COMMIT_WEIGHTS
    rng = rng_for_day(f"{day_key}:target")
    pick = rng.random()
    cumulative = 0

    for count, weight in weights.items():
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
        return min(remaining, max(1, target // 2), MAX_COMMITS_PER_RUN)

    return min(remaining, MAX_COMMITS_PER_RUN)


def last_commit_message():
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def choose_commit_message(previous_message):
    choices = [message for message in messages if message != previous_message]
    return random.choice(choices or messages)


now = datetime.now(timezone.utc)
today = now.date()
day_key = today.isoformat()
target_commits = weighted_daily_target(today)
already_done = count_today_entries(day_key)
commits_this_run = planned_commits_for_run(target_commits, already_done, now)

if commits_this_run == 0:
    print(f"No activity commit needed today ({already_done}/{target_commits}).")
    raise SystemExit(0)

# Random delay: 0–20 minutes, to make commit times look natural.
delay_seconds = random.randint(0, 20 * 60)
time.sleep(delay_seconds)

# Commit messages pool — picked randomly for variety.
messages = [
    "Update notes",
    "Refresh log",
    "Tidy activity file",
    "Sync heartbeat",
    "Record checkpoint",
    "Minor maintenance",
    "Adjust notes",
    "Update tracker",
    "Refresh heartbeat",
    "Log checkpoint",
    "Small cleanup",
    "Sync notes",
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

previous_message = last_commit_message()

for index in range(commits_this_run):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(HEARTBEAT_PATH, "a") as f:
        f.write(f"{timestamp}\n")

    message = choose_commit_message(previous_message)
    subprocess.run(["git", "add", HEARTBEAT_PATH], check=True)
    subprocess.run(
        ["git", "commit", "--author", f"{git_name} <{git_email}>", "-m", message],
        check=True,
        env=git_env,
    )
    previous_message = message

    if index < commits_this_run - 1:
        time.sleep(random.randint(5 * 60, 20 * 60))

print(f"Created {commits_this_run} activity commit(s) ({already_done + commits_this_run}/{target_commits} today).")
