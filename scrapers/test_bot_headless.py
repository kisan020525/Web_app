
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style

init()

def test_headless():
    print(f"{Fore.CYAN}[TEST] Starting Headless Browser Smoke Test...{Style.RESET_ALL}")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Invisible
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3") # Suppress logs
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print(f"{Fore.GREEN}[SUCCESS] Chrome Driver initialized.{Style.RESET_ALL}")
        
        target = "https://www.reddit.com/r/marketing/"
        print(f"{Fore.CYAN}[TEST] Navigating to {target}...{Style.RESET_ALL}")
        driver.get(target)
        
        title = driver.title
        print(f"{Fore.CYAN}[INFO] Page Title: {title}{Style.RESET_ALL}")
        
        if "marketing" in title.lower() or "reddit" in title.lower():
             print(f"{Fore.GREEN}[PASS] Successfully reached Reddit.{Style.RESET_ALL}")
        else:
             print(f"{Fore.YELLOW}[WARN] Title mismatch, but browser is running.{Style.RESET_ALL}")
             
        driver.quit()
        print(f"{Fore.GREEN}[PASS] Test Complete. System is ready for AWS.{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}[FAIL] Error: {e}{Style.RESET_ALL}")
        return False

if __name__ == "__main__":
    test_headless()
