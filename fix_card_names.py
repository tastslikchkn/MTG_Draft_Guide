#!/usr/bin/env python3
"""
Fix corrupted HTML and update card names:
- "Scathing Shadowlock" -> "Scathing Shadelock"
- "Abigail, the Witch" -> "Abigale, Poet Laureate"
"""
import re

def fix_html():
    with open('./strixhaven-draft-guide.html', 'r') as f:
        content = f.read()
    
    # Fix card name 1: Scathing Shadowlock -> Scathing Shadelock
    content = content.replace('Scathing Shadowlock', 'Scathing Shadelock')
    
    # Fix card name 2: Abigail, the Witch -> Abigale, Poet Laureate
    content = content.replace('Abigail, the Witch', 'Abigale, Poet Laureate')
    
    with open('./strixhaven-draft-guide.html', 'w') as f:
        f.write(content)
    
    print("✅ Fixed card names in strixhaven-draft-guide.html")

if __name__ == "__main__":
    fix_html()
