
# AWS Traffic Bot Deployment Instructions

## Prerequisites (On Your AWS Windows Server)
1.  **Google Chrome:** Must be installed.
2.  **Python:** Must be installed (with "Add to PATH" checked).

## Installation
1.  Unzip `traffic_bot_aws.zip` into a folder (e.g., `C:\TrafficBot`).
2.  Open Command Prompt (cmd) or PowerShell in that folder.
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Bot (24/7 AUTONOMOUS MODE)
1.  Run the bot:
    ```bash
    python browser_bot_ai.py
    ```
2.  **IMPORTANT:**
    - The bot is FULLY AUTOMATIC. It will decide to post or skip on its own.
    - It runs on a loop (checks every 5 minutes).
    - It uses "Javascript Deep Clicks" to bypass Reddit errors.
    - **First Run:** You still need to log in manually once.
    - The bot will detect your API Key from the included .env file.
    - The first time, a Chrome window will open.
    - You MUST log in to Reddit manually.
    - After login, press ENTER in the console.
    - The bot will now run and search for leads.

## Tips
- Do not close the Chrome window.
- If you disconnect from RDP, ensure your session stays active (use a "Keep Alive" script or just don't log off, only disconnect).
