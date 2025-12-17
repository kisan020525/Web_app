
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
# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyDDVn8NFcByjaOh4BoDok1AfXccn4zGsBE"

# Configure Gemini
try:
    print(f"🔑 Configuring Gemini with Key ending in: ...{GEMINI_API_KEY[-4:]}")
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"⚠️ Gemini Config Error: {e}")

class TrendEngineV2:
    def __init__(self):
        self.site_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        # Using real 'trends' directory for production, or 'trends_dev' for testing
        self.trends_dir = os.path.join(self.site_root, 'trends') 
        if not os.path.exists(self.trends_dir):
            os.makedirs(self.trends_dir)
        print(f"🤖 TrendEngine 2.0 Output Dir: {self.trends_dir}")
        self.load_template()

    def load_template(self):
        """Loads the NEW News/Editorial HTML template."""
        # Using the new template file we just created
        template_path = os.path.join(self.site_root, 'templates', 'news-article-template.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.template_html = f.read()
            print("✅ News Article Template Loaded.")
        except Exception as e:
            print(f"❌ Template Load Error: {e}")
            self.template_html = "<html><body><h1>Error: Template Missing</h1></body></html>"

    def scan_deep_trends(self):
        """
        Step 1: Get Real-Time Trends from Google News RSS.
        Reliable Source: https://news.google.com/rss/search?q=technology
        """
        print("📡 Scanning Real-Time News (30+ Sources)...")
        candidates = []
        try:
            import requests
            import xml.etree.ElementTree as ET
            
            # Google News RSS (Technology / India)
            rss_url = "https://news.google.com/rss/search?q=technology&hl=en-IN&gl=IN&ceid=IN:en"
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            response = requests.get(rss_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text
                    # Clean title (Remove source name like ' - Reuters')
                    clean_title = title.split(' - ')[0]
                    candidates.append(clean_title)
                
                print(f"✅ Found {len(candidates)} fresh news items.")
            else:
                print(f"⚠️ RSS Failed (Status {response.status_code}). Switching to fallback.")
            
            # Deduplicate and limit
            candidates = list(set(candidates))[:50]
            
            if not candidates:
                 raise Exception("No news found in RSS.")
                 
            return candidates
    
        except Exception as e:
            print(f"⚠️ Scan Error: {e}")
            return ["DeepSeek vs OpenAI", "Indian SaaS Growth 2025", "NVIDIA vs AMD Stock", "AI Agents for Business"] # Fallback

    def ai_thinker_select_one(self, candidates):
        """
        Step 2: The 'Thinker' - Pick ONLY ONE best trend for NEWS REPORTING.
        User Request: "Not affilaite... just give information... work as news provider"
        """
        if not candidates:
             print("⚠️ No candidates found. Using emergency fallback.")
             candidates = ["DeepSeek", "ChatGPT-5", "NVIDIA AI"]

        print("🧠 'Thinker' Mode: Analyzing 50 trends for Breaking Tech News...")
        
        prompt = f"""
        Act as a Tech News Editor.
        I have a list of trending topics in India/Tech:
        {candidates}
        
        Your Goal: Pick EXACTLY ONE topic that is:
        1. "Breaking News" worthy (high curiosity).
        2. Relevant to Tech/AI/Business.
        3. Educational/Informative.
        
        Ignore: Salesy software reviews. We want pure information/news.
        
        Return ONLY the topic name as a plain string. Nothing else.
        """
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite') 
            res = model.generate_content(prompt)
            chosen_topic = res.text.strip().replace('"', '').replace("'", "")
            print(f"🎯 Thinker Selected: {chosen_topic}")
            return chosen_topic
        except Exception as e:
            print(f"⚠️ Thinker Fallback (API Error): {e}")
            return candidates[0]

    def generate_grounded_page(self, topic):
        """
        Step 3 & 6: Search Grounding + Image Sourcing + News Template.
        Using Gemini Tools: google_search
        """
        print(f"✍️ Generating Full HTML for: {topic} (Grounding Enabled)...")
        
        # Test 'google_search' string (Standard in 1.5+)
        tools = 'google_search' 
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash-lite', tools=tools)
        except Exception as e:
            print(f"⚠️ Tool Init Error: {e}")
            model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        prompt = f"""
        Act as a Tech Reporter (News Only).
        Topic: "{topic}" 
        
        Task: Write a high-quality Breaking News Article about this topic.
        Target Audience: Tech enthusiasts, Founders, Developers.
        Style: Informative, Unbiased, "TechCrunch" style. NO SALES.
        
        Use this EXACT HTML TEMPLATE structure:
        
        {self.template_html}
        
        INSTRUCTIONS:
        1. {{HEADLINE}}: Catchy news headline (e.g. "Why X is Exploding...").
        2. {{SUBTITLE}}: 2-sentence summary/hook.
        3. {{DATE_PUBLISHED}}: Today's date (e.g. Dec 16, 2025).
        4. {{SUMMARY_SNIPPET}}: Meta description.
        5. {{KEY_POINTS_LIST_ITEMS}}: 3-4 <li> items summarizing the key facts.
        6. {{ARTICLE_CONTENT_HTML}}: The full article body (approx 600 words). Use <h2> for subheadings and <p> for text. Focus on "What happened", "Why it matters", "What's next".
        
        Output: ONLY Valid HTML code with placeholders filled.
        """
        
        try:
            response = model.generate_content(prompt)
            # Gemini might return grounded metadata, we want the text (HTML)
            html = response.text.replace("```html", "").replace("```", "")
            return html
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            return None

    def publish_and_inject(self, topic, html_content):
        """
        Step 4 & 7: Save file as Clean URL (slug/index.html), Update Hub, Update Nav.
        """
        if not html_content or len(html_content) < 500:
            print("⚠️ Content too short or empty. Aborting publish.")
            return

        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Create URL-safe slug (remove all Windows-invalid characters)
        import re
        slug = topic.lower()
        slug = re.sub(r'[:\'"*?<>|/\\]', '', slug)  # Remove invalid Windows chars
        slug = slug.replace(" ", "-").replace(".", "")
        slug = re.sub(r'-+', '-', slug)  # Remove duplicate dashes
        slug = slug.strip('-')[:40]  # Trim and limit length
        
        # 1. Create Directory for Clean URL: trends/slug/
        page_dir = os.path.join(self.trends_dir, slug)
        if not os.path.exists(page_dir):
            os.makedirs(page_dir)
            
        filename = "index.html"
        filepath = os.path.join(page_dir, filename)
        
        # FIX RELATIVE PATHS:
        # Template assumes it's in trends/page.html (depth 1), so using "../css/"
        # Now it is in trends/slug/index.html (depth 2), need "../../css/"
        html_content = html_content.replace('href="../css/', 'href="../../css/')
        html_content = html_content.replace('src="../js/', 'src="../../js/')
        html_content = html_content.replace('src="../assets/', 'src="../../assets/')
        html_content = html_content.replace('href="../index.html"', 'href="../../index.html"')
        
        # Save HTML
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"💾 Saved Clean URL: trends/{slug}/")
        
        # Inject into Hub and Nav
        self.update_hub_page(topic, f"{slug}/", date_str)
        self.update_navbar(topic, f"trends/{slug}/")
        
        # [NEW] SEO & Ticker Optimization
        self.update_sitemap(slug)
        self.update_homepage_feed(topic, f"trends/{slug}/", date_str)
        
        return slug

    def update_sitemap(self, slug):
        """
        Appends the new clean URL to sitemap.xml for Google Indexing.
        """
        sitemap_path = os.path.join(self.site_root, "sitemap.xml")
        try:
            with open(sitemap_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Simple append before </urlset>
            new_url = f"""
    <url>
        <loc>https://angyone.com/trends/{slug}/</loc>
        <lastmod>{datetime.datetime.now().strftime("%Y-%m-%d")}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>"""
            
            if slug not in content:
                if "</urlset>" in content:
                    content = content.replace("</urlset>", new_url + "\n</urlset>")
                    with open(sitemap_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print("✅ SEO: Added to Sitemap.")
        except Exception as e:
            print(f"❌ Sitemap Update Error: {e}")

    def update_homepage_feed(self, topic, link, date_str):
        """
        Injects a 'Breaking News' card into the index.html ticker.
        Target: <!-- DYNAMIC_NEWS_FEED -->
        """
        index_path = os.path.join(self.site_root, "index.html")
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            marker = '<!-- DYNAMIC_NEWS_FEED -->'
            
            # Simple Card Design
            new_card = f"""
            <div class="news-card" style="background: var(--bg-main); padding: 16px; border-radius: 8px; border: 1px solid var(--border);">
                <div style="font-size: 0.75rem; opacity: 0.6; margin-bottom: 8px;">{date_str}</div>
                <h4 style="margin: 0; font-size: 1rem; line-height: 1.4;">
                    <a href="{link}" style="color: var(--text-main); text-decoration: none;">{topic}</a>
                </h4>
            </div>
            """
            
            if marker in content:
                # Prepend to keep freshest first? OR Append?
                # Let's prepend to the marker so it appears first if we structure it right,
                # actually 'replace marker with marker + new' puts it after.
                # To make it appear top/left, we should insert AFTER the marker.
                # And since regular grid flows left-to-right, new items will appear first if we insert them immediately after marker.
                
                # Check dupe
                if link in content:
                    return

                replacement = f'{marker}\n{new_card}'
                new_content = content.replace(marker, replacement)
                
                with open(index_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print("✅ Homepage: Added to News Ticker.")
                
        except Exception as e:
            print(f"❌ Ticker Update Error: {e}")

    def update_hub_page(self, topic, link_href, date_str):
        # (Simplified Hub Injection Logic - Same as v1 but robust)
        hub_path = os.path.join(self.trends_dir, "index.html")
        if not os.path.exists(hub_path):
            with open(hub_path, "w", encoding="utf-8") as f:
                f.write(f"""
                <html><head><link rel="stylesheet" href="../css/styles.css"></head>
                <body><div class="container"><h1>Global Trend Feed</h1><div id="trend-feed"></div></div></body></html>
                """)
        
        with open(hub_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        new_entry = f"""
        <div class="trend-card" style="margin-bottom: 20px; border-bottom: 1px solid #333; padding-bottom: 20px;">
            <div style="font-size: 0.8rem; opacity: 0.6;">{date_str}</div>
            <h3><a href="{link_href}">{topic}</a></h3>
        </div>
        """
        
        if '<div id="trend-feed">' in content:
            new_content = content.replace('<div id="trend-feed">', '<div id="trend-feed">' + new_entry)
            with open(hub_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("✅ Hub Feed Updated.")

    def update_navbar(self, topic, link_href):
        """
        Previously injected individual links into Trends dropdown.
        Now simplified: Articles are discoverable via 'Live Feed' link to trends hub.
        This prevents navbar overflow with 12+ articles/day.
        """
        # No longer add individual links to dropdown to prevent overflow
        # The hub page (trends/index.html) shows all articles
        print(f"ℹ️ Article added to Hub Page (Navbar simplified - use 'Live Feed' link).")

    
    def push_to_github(self, created_slugs=None):
        """
        Pushes changes to GitHub using REST API (No Git required).
        Only pushes specific files that were created/modified in this run.
        """
        print("🐙 Starting GitHub Sync (API Mode)...")
        
        # Configuration - Token from Environment Variable
        GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
        if not GITHUB_TOKEN:
            print("⚠️ GITHUB_TOKEN not set. Skipping push. Set it with: set GITHUB_TOKEN=your_token")
            return
        REPO_OWNER = "kisan020525"
        REPO_NAME = "Web_app"
        BRANCH = "main"
        
        import requests
        import base64
        
        api_base = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            # Build list of files to push (only what was created this run)
            files_to_push = []
            
            # Add specific trend files that were created
            if created_slugs:
                for slug in created_slugs:
                    trend_file = os.path.join(self.site_root, "trends", slug, "index.html")
                    if os.path.exists(trend_file):
                        files_to_push.append((trend_file, f"trends/{slug}/index.html"))
            
            # Add trends/index.html (hub page)
            hub_file = os.path.join(self.site_root, "trends", "index.html")
            if os.path.exists(hub_file):
                files_to_push.append((hub_file, "trends/index.html"))
            
            # Add sitemap (always updated with new URLs)
            files_to_push.append((os.path.join(self.site_root, "sitemap.xml"), "sitemap.xml"))
            
            pushed_count = 0
            for local_path, github_path in files_to_push:
                if not os.path.exists(local_path):
                    continue
                    
                with open(local_path, "rb") as f:
                    content = base64.b64encode(f.read()).decode()
                
                # Get current file SHA (if exists)
                sha = None
                check_url = f"{api_base}/contents/{github_path}?ref={BRANCH}"
                resp = requests.get(check_url, headers=headers)
                if resp.status_code == 200:
                    sha = resp.json().get("sha")
                
                # Create/Update file
                update_url = f"{api_base}/contents/{github_path}"
                data = {
                    "message": f"Auto-Update: {github_path}",
                    "content": content,
                    "branch": BRANCH
                }
                if sha:
                    data["sha"] = sha
                
                resp = requests.put(update_url, headers=headers, json=data)
                if resp.status_code in [200, 201]:
                    pushed_count += 1
                else:
                    print(f"⚠️ Failed to push {github_path}: {resp.status_code}")
            
            print(f"✅ Pushed {pushed_count} files to GitHub.")
            
        except Exception as e:
            print(f"❌ GitHub API Error: {e}")

    def run_daily_cycle(self):
        print("🚀 Starting Trend Engine v2.0 (Batch Mode)...")
        # 1. Scan
        candidates = self.scan_deep_trends()
        
        if not candidates:
            print("⚠️ No topics found. Exiting.")
            return

        # [NEW] History Guard: Don't repeat topics covered recently
        history_path = os.path.join(self.site_root, "trend_history.log")
        covered_topics = []
        if os.path.exists(history_path):
            with open(history_path, "r", encoding="utf-8") as f:
                covered_topics = f.read().splitlines()
        
        # Filter candidates against history
        # (Fuzzy matching or exact string? Let's use exact string for news titles)
        filtered_candidates = [c for c in candidates if c not in covered_topics]
        
        if not filtered_candidates:
            print("⏳ All current trends have been covered. Waiting for fresh news...")
            return

        # Generator Loop: Create 1 Article per Run (Scheduler Friendly)
        MAX_ARTICLES = 1

        generated_count = 0
        used_topics = []
        created_slugs = []  # [NEW] Track slugs created this run
        
        while generated_count < MAX_ARTICLES:
            print(f"\n--- 🔄 Generating {generated_count+1}/{MAX_ARTICLES} ---")
            
            # Filter candidates against run-session used_topics AND global history
            # Note: filtered_candidates already filtered Global History.
            # We just need to filter 'used_topics' (this run).
            current_candidates = [c for c in filtered_candidates if c not in used_topics]
            
            if not current_candidates:
                print("⚠️ No more unique candidates.")
                break
                
            # Pick Topic (News Focus)
            topic = self.ai_thinker_select_one(current_candidates)
            if topic in used_topics:
                print(f"⚠️ Duplicate topic {topic} selected. Skipping.")
                continue
                
            used_topics.append(topic)
            
            # Generate
            html = self.generate_grounded_page(topic)
            if html:
                slug = self.publish_and_inject(topic, html)
                if slug:
                    generated_count += 1
                    created_slugs.append(slug)  # [NEW] Track the slug
                    # Log to History immediately
                    with open(history_path, "a", encoding="utf-8") as f:
                        f.write(topic + "\n")
                    time.sleep(2) # Politeness delay
        
        print(f"\n🏁 Batch Complete. Generated {generated_count} articles.")
        
        if generated_count > 0:
            self.push_to_github(created_slugs)  # [NEW] Pass slugs to push

if __name__ == "__main__":
    engine = TrendEngineV2()
    engine.run_daily_cycle()
