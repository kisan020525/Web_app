import google.generativeai as genai
import os
import datetime
import time
import subprocess
try:
    from pytrends.request import TrendReq
except ImportError:
    print("⚠️ pytrends not installed. Run: pip install pytrends pandas")
    TrendReq = None

# --- CONFIGURATION ---
GOOGLE_SEARCH_API_KEY = "AIzaSyCLS_mgYXyyZBZXurEBeMxbvQe5q3NvGZk" # User Provided
GOOGLE_SEARCH_CX = "e51ec8cb44bd54574" # Configured ✅
GEMINI_API_KEY = "AIzaSyByC8Le1NRDhpzfjOwTGavCSgyip7lD14k" # User Provided

# Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"⚠️ Gemini Config Error: {e}")

class TrendEngine:
    def __init__(self):
        self.site_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # TESTING MODE: Output to separate folder
        self.trends_dir = os.path.join(self.site_root, 'trends_test')
        if not os.path.exists(self.trends_dir):
            os.makedirs(self.trends_dir)
        print(f"🤖 TrendEngine Output Dir: {self.trends_dir}")

    def get_rising_trends(self):
        """
        Step 1: Detect Trends using PYTRENDS (Free).
        """
        print("📊 Connecting to Google Trends via Pytrends...")
        
        if not TrendReq:
            print("❌ Pytrends library missing. Using Mock Data.")
            return [{"query": "DeepSeek vs ChatGPT", "velocity": "Mock High"}]

        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            trending_searches_df = pytrends.trending_searches(pn='united_states')
            top_trends = trending_searches_df.head(3)[0].tolist()
            print(f"🔥 Detected Trends: {top_trends}")
            return [{"query": t, "velocity": "High"} for t in top_trends]
        except Exception as e:
            print(f"⚠️ Pytrends Error: {e}")
            return [{"query": "AI Marketing Tools 2025", "velocity": "Fallback"}]

    def research_topic(self, topic):
        """
        Step 2: Gather Ground Truth (Google Custom Search API).
        """
        print(f"🔍 Researching topic: {topic}...")
        
        if "YOUR_SEARCH_ENGINE_ID" in GOOGLE_SEARCH_CX:
             print("⚠️ Missing Search Engine ID (CX). Using Mock Data.")
             return {"summary": f"Research for {topic} (Mock).", "source": "Mock"}

        try:
            import requests
            url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_SEARCH_API_KEY}&cx={GOOGLE_SEARCH_CX}&q={topic}"
            res = requests.get(url).json()
            
            if 'items' in res:
                snippets = [item['snippet'] for item in res['items'][:3]]
                summary = " ".join(snippets)
                print(f"✅ Found {len(snippets)} sources.")
                return {"summary": summary, "source": "Google API"}
            else:
                print("⚠️ No results found via API.")
                return {"summary": f"No detailed research found for {topic}.", "source": "None"}
                
        except Exception as e:
            print(f"⚠️ Search API Error: {e}")
            return {"summary": f"Research failed for {topic}.", "source": "Error"}

    def generate_article(self, topic, research_data):
        """
        Step 3: AI Writing (Gemini 2.5 Flash Lite).
        """
        print(f"✍️ Asking Gemini (2.5-flash-lite) to write about: {topic}...")
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""
        Act as an expert tech journalist for AngyOne.
        Write a full HTML page analyzing this trend: '{topic}'.
        
        Research Context:
        {research_data['summary']}
        
        Requirements:
        1. Use the AngyOne HTML structure (Navbar, Hero, Container).
        2. Tone: Skeptical, data-driven, "Stress Test" style.
        3. Include a "Why it matters" section.
        4. Return ONLY the HTML code, no markdown backticks.
        """

        try:
            # Using the specific model requested by the user
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            response = model.generate_content(prompt)
            html_content = response.text
            
            # Basic cleanup if model adds markdown
            html_content = html_content.replace("```html", "").replace("```", "")
            return html_content
            
        except Exception as e:
            print(f"⚠️ Gemini Generation Error: {e}")
            # Fallback template if AI fails
            return f"<html><body><h1>Error generating content for {topic}</h1><p>{e}</p></body></html>"

    def publish_article(self, topic, html_content):
        """
        Step 4: Save to File.
        """
        slug = topic.lower().replace(" ", "-")[:50] # Limit filename length
        filename = f"{slug}.html"
        filepath = os.path.join(self.trends_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"[DONE] Saved HTML: {filename}")
        
        # Step 4b: Update the Hub Page
        self.update_trends_hub(topic, filename, datetime.datetime.now().strftime("%Y-%m-%d"))
        
        # Step 4c: Update the Global Navigation
        self.update_global_nav(topic, filename)
        
        return filename

    def update_trends_hub(self, topic, filename, date_str):
        """
        Step 4b: Safely inject link into trends/index.html
        """
        hub_path = os.path.join(self.trends_dir, "index.html")
        if not os.path.exists(hub_path):
            print("[WARN] Hub page not found. Skipping link injection.")
            return

        print(f"[LINK] Updating Hub Page: {hub_path}")
        try:
            with open(hub_path, "r", encoding="utf-8") as f:
                content = f.read()

            # The Card to Inject
            new_card = f"""
                <!-- {topic} -->
                <article class="trend-card">
                    <div class="trend-meta">
                        <span class="trend-badge">New Arrival</span>
                        <time>{date_str}</time>
                    </div>
                    <h2 class="trend-title"><a href="{filename}" style="text-decoration: none; color: inherit;">{topic}</a></h2>
                    <p class="trend-snippet">Latest market intelligence generated by AngyOne Autonomous Engine.</p>
                    <a href="{filename}" style="color: var(--primary); font-weight: 600; text-decoration: none;">Read Report →</a>
                </article>
            """

            # Injection Point: After <div id="trend-feed">
            if '<div id="trend-feed">' in content:
                updated_content = content.replace('<div id="trend-feed">', '<div id="trend-feed">' + new_card)
                
                with open(hub_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print("[DONE] Hub Page Updated!")
            else:
                print("[WARN] Could not find insertion point <div id='trend-feed'>")

        except Exception as e:
            print(f"[ERROR] Failed to update hub: {e}")

    def update_global_nav(self, topic, filename):
        """
        Step 4c: Update the Logic for Main Menu Injection.
        """
        index_path = os.path.join(self.site_root, "index.html")
        
        if not os.path.exists(index_path):
            print(f"[WARN] Index page not found at {index_path}. Skipping nav injection.")
            return

        print(f"[LINK] Updating Global Nav: {index_path}")
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Use relative path for main menu
            rel_link = f"trends/{filename}"
            new_link = f'<a href="{rel_link}">{topic}</a>'
            
            # Injection Point: <a href="trends/">Live Feed</a>
            target = '<a href="trends/">Live Feed</a>'
            
            if target in content:
                # Add BEFORE the "Live Feed" link
                updated_content = content.replace(target, new_link + "\n                        " + target)
                
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(updated_content)
                print("[DONE] Global Nav Updated!")
            else:
                print("[WARN] Could not find 'Live Feed' link in index.html to attach to.")

        except Exception as e:
            print(f"[ERROR] Failed to update nav: {e}")

    def git_push(self):
        """
        Step 5: AWS Deployment Sync.
        """
        print("[SYNC] Syncing to GitHub...")
        try:
            subprocess.run(["git", "add", "."], cwd=self.site_root, check=True)
            subprocess.run(["git", "commit", "-m", "TrendEngine Auto-Publish"], cwd=self.site_root, check=True)
            subprocess.run(["git", "push"], cwd=self.site_root, check=True)
            print("[DONE] Successfully pushed to GitHub Pages!")
        except Exception as e:
            print(f"[WARN] Git Sync Failed: {e}")

    def run_agentic_cycle(self):
        print("[START] Starting Trend Engine (Agentic Mode)...")
        
        # 1. SCOUT: Get Raw Candidates
        candidates = self.get_rising_trends() # Returns list of strings
        if not candidates:
            print("[SLEEP] No trends found.")
            return

        # 2. EDITOR: AI Decides what's worth writing
        print(f"[AI] AI Editor analyzing {len(candidates)} candidates...")
        selected_topics = self.ai_select_best_trends(candidates)
        
        # 3. EXECUTE: Loop through the chosen few (Max 2)
        for topic in selected_topics[:2]:
            print(f"[PROC] Processing Appproved Topic: {topic}")
            
            # 3a. STRATEGIST: Ask AI what to search
            search_query = self.ai_generate_search_query(topic)
            
            # 3b. RESEARCHER: Execute Search
            research_data = self.research_topic(search_query)
            
            # 3c. WRITER: Generate Content
            html = self.generate_article(topic, research_data)
            self.publish_article(topic, html)

    def get_rising_trends(self):
        """
        Step 1: Detect Trends using Google Trends RSS (India).
        """
        print("[INFO] Fetching Indian trends via RSS...")
        import requests
        import xml.etree.ElementTree as ET

        try:
            # RSS Feed for India
            rss_url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=IN"
            response = requests.get(rss_url)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                trends = []
                # Parse XML
                for item in root.findall('.//item'):
                    title = item.find('title').text
                    trends.append(title)
                
                print(f"[DATA] Detected India Trends: {trends[:5]}")
                return trends
            else:
                 print(f"[WARN] RSS Failed: {response.status_code}")
                 
        except Exception as e:
            print(f"[ERROR] Trend Detection Error: {e}")
        
        print("[WARN] Using Fallback Trend List.")
        return ["Zepto vs Blinkit", "Zoho pricing", "Indian SaaS 2025", "UPI updates"]

    def ai_select_best_trends(self, candidates):
        """Step 2: AI Filters the list (Indian Context)"""
        prompt = f"""
        You are the Editor-in-Chief of 'AngyOne India'.
        Here is a list of potential trending topics in India:
        {candidates}
        
        Pick the TOP 2 topics that are most relevant to: 
        1. Technology / AI
        2. Business / Startups (e.g., IPOs, earnings)
        3. Marketing / SaaS
        
        Ignore: Politics, Bollywood, Cricket (unless it implies a major tech/business angle).
        
        Return ONLY a Python list of strings, e.g.: ["Topic A", "Topic B"]
        """
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            res = model.generate_content(prompt)
            # clean cleanup to get list
            clean_text = res.text.replace("```json", "").replace("```python", "").replace("```", "").strip()
            # Simple fallback parsing if calc fails
            if "[" in clean_text:
                return eval(clean_text) 
            return candidates[:2] 
        except Exception as e:
            print(f"[WARN] AI Filter Error: {e}")
            return candidates[:2]

    def ai_generate_search_query(self, topic):
        """Step 3a: AI crafts the perfect search query"""
        prompt = f"For the topic '{topic}', write ONE exact Google Search query to find recent facts, pricing, or controversy. Return ONLY the query."
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
            res = model.generate_content(prompt)
            return res.text.strip().replace('"', '')
        except:
            return topic # Fallback


if __name__ == "__main__":
    engine = TrendEngine()
    # engine.run_cycle() # Old mode
    engine.run_agentic_cycle() # New Agentic Mode
