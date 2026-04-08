#!/usr/bin/env python3
"""
activity_bot.py — appends a timestamp to heartbeat.txt and commits it.
Run directly or via GitHub Actions.
"""

import subprocess
import random
import time
from datetime import datetime, timezone

# Random delay: 0–20 minutes, to make commit times look natural
delay_seconds = random.randint(0, 20 * 60)
time.sleep(delay_seconds)

# Append timestamp
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
with open("heartbeat.txt", "a") as f:
    f.write(f"{timestamp}\n")

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
message = random.choice(messages)

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
subprocess.run(["git", "add", "heartbeat.txt"], check=True)
subprocess.run(
    ["git", "commit", "--author", f"{git_name} <{git_email}>", "-m", message],
    check=True,
    env=git_env,
)
