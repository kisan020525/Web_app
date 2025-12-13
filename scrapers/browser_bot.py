
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style

# Initialize Colorama
init()

def print_status(message, status="INFO"):
    if status == "INFO":
        print(f"{Fore.CYAN}[INFO]{Style.RESET_ALL} {message}")
    elif status == "SUCCESS":
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {message}")
    elif status == "WARNING":
        print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {message}")
    elif status == "ERROR":
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {message}")

def start_browser_agent():
    print_status("Initializing Browser Agent...", "INFO")
    
    # Setup Chrome Options
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Commented out so user can see the agent working
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print_status("Browser Launched!", "SUCCESS")
        
        # 1. Login Phase
        print_status("Navigating to Reddit Login...", "INFO")
        driver.get("https://www.reddit.com/login/")
        
        print_status("⚠️  ACTION REQUIRED: Please Log In manually in the browser window.", "WARNING")
        input(f"{Fore.YELLOW}Press ENTER here after you have successfully logged in...{Style.RESET_ALL}")
        
        # 2. Search Phase
        keywords = ["Mailchimp pricing", "Mailchimp alternatives", "Mailchimp expensive"]
        
        for keyword in keywords:
            print_status(f"Agent searching for: '{keyword}'", "INFO")
            search_url = f"https://www.reddit.com/search/?q={keyword.replace(' ', '%20')}&t=week"
            driver.get(search_url)
            time.sleep(3) # Let page load
            
            # Here we would identify posts. For safety/demo, we just scroll.
            driver.execute_script("window.scrollTo(0, 500);")
            time.sleep(2)
            
            print_status(f"Scanned page for '{keyword}'.", "SUCCESS")
            
            # In a full bot, we would:
            # 1. Find elements with class "Post"
            # 2. Click them
            # 3. Click Reply
            # 4. Paste text
            
            cont = input(f"{Fore.CYAN}Search next keyword? (y/n): {Style.RESET_ALL}")
            if cont.lower() != 'y':
                break
                
        print_status("Mission Complete. Closing Agent.", "SUCCESS")
        driver.quit()
        
    except Exception as e:
        print_status(f"Agent Failure: {e}", "ERROR")

if __name__ == "__main__":
    # Check for libraries
    try:
        import selenium
        import webdriver_manager
        start_browser_agent()
    except ImportError:
        print_status("Missing dependencies. Installing...", "WARNING")
        os.system("pip install selenium webdriver-manager colorama")
        print_status("Dependencies installed. Please run script again.", "SUCCESS")
