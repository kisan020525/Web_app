
import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore, Style
import google.generativeai as genai
from dotenv import load_dotenv

# Initialize Colorama
init()
load_dotenv()

# --- CONFIGURATION ---
MODEL_NAME = "gemini-2.5-flash-lite"
TARGET_SUBREDDITS = ["marketing", "smallbusiness", "entrepreneur", "emailmarketing"]
SEARCH_KEYWORDS = ["Mailchimp pricing", "Mailchimp expensive", "Mailchimp alternatives", "best email marketing"]

def print_status(message, status="INFO"):
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "BRAIN": Fore.MAGENTA,
        "ACTION": Fore.BLUE
    }
    print(f"{colors.get(status, Fore.WHITE)}[{status}] {message}{Style.RESET_ALL}")

def setup_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_status("GEMINI_API_KEY not found in .env", "WARNING")
        sys.exit(1)
        
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        print_status(f"Connected to Brain: {MODEL_NAME}", "SUCCESS")
        return model
    except Exception as e:
        print_status(f"Failed to connect to AI: {e}", "ERROR")
        sys.exit(1)

def generate_reply(model, post_title, post_body=""):
    print_status("Reading post content...", "BRAIN")
    
    prompt = f"""
    You are representing "AngyOne", a helpful resource for marketers.
    
    **Your Knowledge Base:**
    1.  **Main Comparison:** angyone.cloud/comparisons/brevo-vs-mailchimp/
        *   BEST FOR: Complaints about Mailchimp pricing, contacts limits, or "expensive".
        *   KEY FACT: Mailchimp charges for *storage* (inactive contacts). Brevo charges for *sending* (unlimited storage).
    2.  **Guide Hub:** angyone.cloud/guides/
        *   BEST FOR: General questions about how to start email marketing or strategy.
    
    **Context:**
    Reddit Post Title: "{post_title}"
    Reddit Post Body: "{post_body}"
    
    **Task:**
    Decide if we should reply.
    *   IF the user is complaining about cost/limits: Reply with EMPATHY + BREVO RECOMENDATION + COMPARISON LINK.
    *   IF the user is just asking for general advice: Reply with STRATEGY + GUIDE LINK.
    *   IF irrelevant/spam: Reply with "SKIP".
    
    **Output Format:**
    Just the comment text. Nothing else.
    If skipping, just output "SKIP".
    """
    
    try:
        response = model.generate_content(prompt)
        reply_text = response.text.strip()
        print_status(f"Thought generated: '{reply_text[:50]}...'", "BRAIN")
        return reply_text
    except Exception as e:
        print_status(f"Thinking failed: {e}", "ERROR")
        return "SKIP"

def find_and_interact_comment_box(driver, actions, wait):
    print_status("Initiating Nuclear Search for Comment Box (V2)...", "ACTION")

    # Helper to Expand Shadow DOM
    def get_shadow_root(element):
        return driver.execute_script('return arguments[0].shadowRoot', element)

    # Strategy 1: The "Add a Comment" / "Join Conversation" Placeholder (Case Insensitive)
    try:
        # Match any element containing the text (case insensitive trick in XPath 1.0)
        xpath = "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add a comment')] | //*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'join the conversation')]"
        placeholders = driver.find_elements(By.XPATH, xpath)
        for p in placeholders:
            if p.is_displayed():
                driver.execute_script("arguments[0].click();", p) # JS Click is safer
                print_status(f"Clicked Placeholder ({p.text}).", "INFO")
                time.sleep(5)
                break
    except:
        pass

    # Strategy 2: Generic "Reply" Button
    try:
        reply_btns = driver.find_elements(By.XPATH, "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reply')] | //a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reply')]")
        if reply_btns:
            target_btn = reply_btns[-1]
            if target_btn.is_displayed():
                 driver.execute_script("arguments[0].click();", target_btn)
                 print_status("Clicked Generic Reply Button.", "INFO")
                 time.sleep(5)
    except:
        pass

    # Strategy 3: Find Editor (Deep Scan)
    print_status("Hunting for Editor...", "INFO")
    
    # Check 1: shreddit-comment-composer (Shadow DOM)
    try:
        composers = driver.find_elements(By.TAG_NAME, "shreddit-comment-composer")
        for composer in composers:
            shadow = get_shadow_root(composer)
            if shadow:
                inner_div = driver.execute_script("return arguments[0].shadowRoot.querySelector('div.rich-text-editor')", composer)
                if inner_div:
                    print_status("Found Editor in Shadow DOM!", "SUCCESS")
                    return inner_div
    except:
        pass

    # Check 2: Standard ContentEditable
    try:
        element = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true']")
        if element.is_displayed():
            print_status("Found Standard Editor.", "SUCCESS")
            return element
    except:
        pass
        
    # Check 3: Textarea
    try:
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for ta in textareas:
            if ta.is_displayed():
                print_status("Found Textarea.", "SUCCESS")
                return ta
    except:
        pass

    # Strategy 4: Hail Mary (Blind Focus)
    print_status("Specific editor not found. Attempting 'Hail Mary' focus...", "WARNING")
    try:
        # Click body to reset, then Tab to try and hit the box (this is risky but works when selectors fail)
        body = driver.find_element(By.TAG_NAME, "body")
        actions.move_to_element(body).click().send_keys(Keys.TAB).perform()
        time.sleep(1)
        # Return the currently active element as a best guess
        active_elem = driver.switch_to.active_element
        print_status(f"Targeting active element: {active_elem.tag_name}", "WARNING")
        return active_elem
    except:
        pass

    return None

def start_smart_bot():
    model = setup_gemini()
    
    print_status("Launching Autonomous Browser...", "INFO")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    actions = ActionChains(driver)

    try:
        # 1. Login
        driver.get("https://www.reddit.com/login/")
        print_status("Please Log In manually in the browser.", "WARNING")
        input(f"{Fore.YELLOW}Press ENTER after you are logged in...{Style.RESET_ALL}")
        
        # 2. Hunt
        while True: # Infinite Loop for 24/7 Running
            for keyword in SEARCH_KEYWORDS:
                print_status(f"Hunting for: '{keyword}'", "INFO")
                try:
                    search_url = f"https://www.reddit.com/search/?q={keyword.replace(' ', '%20')}&t=week"
                    driver.get(search_url)
                    time.sleep(10) # Wait for results
                    
                    # Find links
                    links = driver.find_elements(By.TAG_NAME, "a")
                    post_urls = []
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "/r/" in href and "/comments/" in href:
                            post_urls.append(href)
                    
                    post_urls = list(set(post_urls))[:5] # Top 5
                    
                    for url in post_urls:
                        print_status(f"Analyzing: {url}", "INFO")
                        driver.get(url)
                        time.sleep(10) # Let post load
                        
                        try:
                            title_element = driver.find_element(By.TAG_NAME, "h1")
                            title_text = title_element.text
                            
                            # Brain Decides
                            reply = generate_reply(model, title_text)
                            
                            if reply and "SKIP" not in reply:
                                print_status("DECISION: POSTING COMMENT", "SUCCESS")
                                
                                # Find Box
                                comment_box = find_and_interact_comment_box(driver, actions, wait)
                                
                                if comment_box:
                                    # Force Focus
                                    driver.execute_script("arguments[0].focus();", comment_box)
                                    time.sleep(2)
                                    comment_box.click() 
                                    time.sleep(2)
                                    
                                    # Type
                                    print_status("Typing...", "ACTION")
                                    actions.move_to_element(comment_box).click().send_keys(reply).perform()
                                    time.sleep(5)
                                    
                                    # Submit
                                    submit_btns = driver.find_elements(By.CSS_SELECTOR, "button[type='submit']")
                                    clicked = False
                                    for btn in submit_btns:
                                        if btn.is_displayed() and "comment" in btn.text.lower():
                                            print_status("Clicking Reply Button...", "ACTION")
                                            btn.click()
                                            clicked = True
                                            break
                                    
                                    if not clicked:
                                        # Fallback for icon-only buttons
                                        if submit_btns:
                                           submit_btns[-1].click() # Try the last submit button
                                           print_status("Clicked fallback submit button.", "WARNING")

                                    print_status("Wait 60s before next post...", "INFO")
                                    time.sleep(60) # Safety Delay
                                else:
                                    print_status("Could not find box. Skipping.", "ERROR")
                            else:
                                print_status("DECISION: SKIP", "INFO")
                                
                        except Exception as e:
                            print_status(f"Analysis Failed: {e}", "WARNING")
                        
                        time.sleep(5)
                        
                except Exception as e:
                     print_status(f"Search Loop Error: {e}", "ERROR")
                     time.sleep(10)
            
            print_status("Cycle Complete. Sleeping 5 mins...", "INFO")
            time.sleep(300)

    except Exception as e:
        print_status(f"Bot Fatal Error: {e}", "ERROR")
        
    finally:
        print_status("Closing session.", "INFO")
        driver.quit()

if __name__ == "__main__":
    start_smart_bot()
