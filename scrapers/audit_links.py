import os
import re
from urllib.parse import unquote

def check_site_integrity(root_dir):
    print(f"🔍 Starting Audit of: {root_dir}")
    layout_issues = []
    broken_links = []
    
    # Walk through all HTML files
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(subdir, file)
                rel_path_from_root = os.path.relpath(file_path, root_dir)
                
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                # 1. Check for Broken Internal Links
                # Find href="..." and src="..."
                links = re.findall(r'(?:href|src)=["\'](.*?)["\']', content)
                
                for link in links:
                    # Ignore external, anchors, mailto, etc.
                    if link.startswith("http") or link.startswith("#") or link.startswith("mailto:") or link.startswith("javascript:"):
                        continue
                        
                    # Resolve path
                    # link might be "../../css/styles.css"
                    # origin is "subdir"
                    
                    # Handle root-relative (rare in static, but possible)
                    if link.startswith("/"):
                        target_path = os.path.join(root_dir, link.lstrip("/"))
                    else:
                        target_path = os.path.join(subdir, link)
                    
                    # Clean URL (remove #anchor and ?query)
                    target_path = target_path.split("#")[0].split("?")[0]
                    target_path = unquote(target_path)
                    
                    # Check existence
                    # Special Case: Directory links "folder/" imply "folder/index.html"
                    if link.endswith("/"):
                         target_path_index = os.path.join(target_path, "index.html")
                         if os.path.exists(target_path_index):
                             continue
                         elif os.path.exists(target_path): # Directory exists but no index?
                             continue
                         else:
                             broken_links.append(f"{rel_path_from_root} -> {link}")
                    
                    elif not os.path.exists(target_path):
                        broken_links.append(f"{rel_path_from_root} -> {link}")

    print("\n--- 🚩 Audit Results ---")
    if broken_links:
        print(f"❌ Found {len(broken_links)} Broken Links:")
        for err in broken_links:
            print(f"  - {err}")
    else:
        print("✅ No Broken Internal Links Found.")

if __name__ == "__main__":
    # Assuming script is in scrapers/, site root is up one level
    site_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    check_site_integrity(site_root)
