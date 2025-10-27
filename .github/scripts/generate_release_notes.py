###############################################
# Author : Jon Brown
# Date   : 2025-10-27
# Version: 0.5
###############################################
import openai
import subprocess
import os
from datetime import datetime
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_commit_messages():
    result = subprocess.run(["git", "log", "-n", "20", "--pretty=format:%s"], capture_output=True, text=True)
    return result.stdout.splitlines()

def generate_summary(commits):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize the following commit messages into a changelog."},
            {"role": "user", "content": "\n".join(commits)}
        ]
    )
    return response['choices'][0]['message']['content']

commits = get_commit_messages()
summary = generate_summary(commits)

with open("RELEASE_NOTES.md", "w") as f:
    f.write(f"# Release Notes ({datetime.now().strftime('%Y-%m-%d')})\n\n")
    f.write(summary)

