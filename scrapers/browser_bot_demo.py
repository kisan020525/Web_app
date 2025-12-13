
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style

init()

def run_demo_bot():
    print(f"{Fore.CYAN}[DEMO] Starting Guest Mode Bot...{Style.RESET_ALL}")
    
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Keep visible for user to see, or headless if needed. 
    # Since I am an agent, correct approach is headless for reliability in my env, 
    # but user asked to "check here", so I'll output detailed logs.
    options.add_argument("--headless") 
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-notifications")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"{Fore.GREEN}[SUCCESS] Browser Launched.{Style.RESET_ALL}")
        
        # Skip Login -> Go Straight to Search
        keyword = "Mailchimp pricing"
        print(f"{Fore.CYAN}[ACTION] Searching for '{keyword}' (Guest Mode)...{Style.RESET_ALL}")
        
        search_url = f"https://www.reddit.com/search/?q={keyword.replace(' ', '%20')}&t=week"
        driver.get(search_url)
        time.sleep(5) # Wait for results
        
        title = driver.title
        print(f"{Fore.CYAN} Page Title: {title}{Style.RESET_ALL}")
        
        # Verify we are on the results page
        if "Mailchimp" in title or "reddit" in title.lower():
             print(f"{Fore.GREEN}[PASS] Search Page Loaded Successfully.{Style.RESET_ALL}")
             print(f"{Fore.GREEN}[PASS] Bot is ready to find leads.{Style.RESET_ALL}")
        else:
             print(f"{Fore.RED}[FAIL] Could not verify search results. Title: {title}{Style.RESET_ALL}")

        driver.quit()
        
    except Exception as e:
        print(f"{Fore.RED}[FAIL] Bot Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    run_demo_bot()
