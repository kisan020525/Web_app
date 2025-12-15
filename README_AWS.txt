# 🚀 AngyOne Agentic Engine - AWS Deployment Guide

You have a "Newsroom in a Box". Here is how to turn it on.

## Phase 1: Installation (Do this once)
1.  **Extract:** Unzip `angyone_aws_deploy.zip` to `C:\angyone-site`.
2.  **Open Terminal:** Search for "PowerShell" -> Right Click -> Run as Administrator.
3.  **Install Brains:** Run this command to install the AI and Google tools:
    `pip install pytrends pandas google-generativeai requests`

## Phase 2: Run The Agent (Manual Test)
To make the AI find a trend, research it, and write a page *right now*:

1.  Open PowerShell in the folder:
    `cd C:\angyone-site`
2.  Run the Engine:
    `python scrapers/trend_engine.py`

**What will happen?**
1.  It will fetch Top 10 trends from Google.
2.  Gemini will pick the best 2.
3.  It will search Google for facts.
4.  It will generate HTML files in the `trends/` folder.

## Phase 3: Automation (Set & Forget)
To make this run every 6 hours automatically:

1.  Open **Task Scheduler** on Windows.
2.  Click "Create Basic Task".
3.  Name: `AngyOne Trend Bot`.
4.  Trigger: `Daily` -> Repeat every `6 hours`.
5.  Action: `Start a Program`.
    *   Program: `python`
    *   Arguments: `C:\angyone-site\scrapers\trend_engine.py`

## Phase 4: Go Live!
Currently, the bot is in **Local Mode** (it saves files but doesn't push to the web).
When you trust it:
1.  Open `scrapers/trend_engine.py`.
2.  Uncomment the line `# self.git_push()`.
3.  Make sure Git is logged in on your server.
