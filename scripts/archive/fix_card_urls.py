#!/usr/bin/env python3
"""
Fix all card image URLs in strixhaven-draft-guide.html
Replace 'Unknown Card' placeholders with actual card names from display text.
"""
import re
from scripts.utils import slugify

def extract_card_name(text):
    """Extract clean card name, removing tags like (CT), (MF), etc."""
    # Remove parenthetical tags at end
    match = re.match(r'^(.+?)\s*\([A-Z]+\)\s*$', text.strip())
    if match:
        return match.group(1).strip()
    return text.strip()

def fix_html():
    with open('./strixhaven-draft-guide.html', 'r') as f:
        content = f.read()
    
    # Pattern to find card items: <div class="card-item..."><img ... alt="...">Card Name</div></div>
    pattern = r'<div class="card-item([^>]*)"><div class="card-image-container"><img class="card-image" src="([^"]+)" alt="([^"]+)">(.*?)</div></div>'
    
    def replace_func(match):
        attrs = match.group(1)
        old_src = match.group(2)
        old_alt = match.group(3)
        card_text = match.group(4).strip()
        
        # Extract clean card name for API
        clean_name = extract_card_name(card_text)
        
        # Build new src URL with actual card name
        new_src = f"https://api.scryfall.com/cards/named?fuzzy={clean_name}&format=image"
        new_alt = clean_name
        
        return f'<div class="card-item{attrs}"><div class="card-image-container"><img class="card-image" src="{new_src}" alt="{new_alt}">{card_text}</div></div>'
    
    # Replace all matches
    new_content = re.sub(pattern, replace_func, content)
    
    with open('./strixhaven-draft-guide.html', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed all card image URLs in strixhaven-draft-guide.html")

if __name__ == "__main__":
    fix_html()
