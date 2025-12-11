import praw
import time
import os
import winsound  # Windows only
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize Colorama
init()

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
SUBREDDITS = [
    "marketing",
    "smallbusiness",
    "entrepreneur",
    "saas",
    "emailmarketing",
    "digitalmarketing",
    "startups",
    "sideproject"
]

KEYWORDS = [
    "email marketing",
    "mailchimp",
    "brevo",
    "sendinblue",
    "klaviyo",
    "convertkit",
    "hubspot",
    "newsletter tool",
    "best email tool",
    "cheaper than mailchimp",
    "mailchimp alternative",
    "elevenlabs",
    "ai voice",
    "text to speech"
]

# --- SETUP ---
def get_reddit_instance():
    """
    Tries to create a Reddit instance.
    You need to get these keys from https://www.reddit.com/prefs/apps
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = "AngyOneAvoidanceBot/1.0"

    if not client_id or not client_secret:
        print(Fore.RED + "ERROR: Missing API Keys." + Style.RESET_ALL)
        print("1. Go to https://www.reddit.com/prefs/apps")
        print("2. Create a 'script' app.")
        print("3. Create a .env file in this folder with:")
        print("   REDDIT_CLIENT_ID=your_id")
        print("   REDDIT_CLIENT_SECRET=your_secret")
        return None

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

def main():
    print(Fore.CYAN + "==========================================")
    print("   🎯 ANGYONE REDDIT SNIPER ACTIVATED 🎯")
    print("==========================================" + Style.RESET_ALL)
    print(f"Watching {len(SUBREDDITS)} subreddits for {len(KEYWORDS)} keywords...")
    print("Waiting for leads... (Press Ctrl+C to stop)")
    print("")

    reddit = get_reddit_instance()
    if not reddit:
        return

    subreddit_str = "+".join(SUBREDDITS)
    subreddit = reddit.subreddit(subreddit_str)

    try:
        # Stream new submissions
        for submission in subreddit.stream.submissions(skip_existing=True):
            process_submission(submission)
    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + "Sniper deactivated." + Style.RESET_ALL)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Wait before retrying

def process_submission(submission):
    """Checks if a post contains any of our keywords."""
    title = submission.title.lower()
    text = submission.selftext.lower()
    
    found_keywords = []
    
    for keyword in KEYWORDS:
        if keyword in title or keyword in text:
            found_keywords.append(keyword)

    if found_keywords:
        alert_user(submission, found_keywords)

def alert_user(submission, keywords):
    """Beeps and prints the lead."""
    # Sound Alert
    try:
        winsound.Beep(1000, 500) # Frequency, Duration
    except:
        pass

    print(Fore.GREEN + f"\n[!] DATA MATCH FOUND: {', '.join(keywords)}" + Style.RESET_ALL)
    print(f"Title: {submission.title}")
    print(f"Sub: r/{submission.subreddit}")
    print(f"Link: {submission.shortlink}")
    print(Fore.YELLOW + "Action: GO REPLY!" + Style.RESET_ALL)
    print("-" * 40)

if __name__ == "__main__":
    main()
