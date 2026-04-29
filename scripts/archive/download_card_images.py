#!/usr/bin/env python3
"""
Download all card images for offline reliability.
Simple approach: extract names from HTML, fetch via Scryfall API, cache locally.
"""
import json
import re
import time
from pathlib import Path
from urllib.parse import quote
import requests

def extract_cards_from_html(html_path: Path) -> list[str]:
    """Extract all unique card names from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Match alt attributes in img tags
    pattern = r'<img[^>]+alt="([^"]+)"'
    matches = re.findall(pattern, content)
    return sorted(set(matches))

def download_card_image(card_name: str) -> bool:
    """
    Download a single card image from Scryfall.
    Returns True on success.
    """
    # Query Scryfall API
    url = f"https://api.scryfall.com/cards/named?fuzzy={quote(card_name)}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"  ⚠️  HTTP {response.status_code} for: {card_name}")
            return False
        
        data = response.json()
        if data.get('object') == 'error':
            print(f"  ⚠️  Card not found: {card_name}")
            return False
        
        # Get image URL (try border_crop first, then normal)
        image_uris = data.get('image_uris', {})
        image_url = image_uris.get('border_crop') or image_uris.get('normal')
        
        if not image_url:
            print(f"  ⚠️  No image for: {card_name}")
            return False
        
        # Download the image
        img_response = requests.get(image_url, timeout=30)
        if img_response.status_code != 200:
            print(f"  ⚠️  Image fetch failed for: {card_name}")
            return False
        
        # Save to local file
        safe_name = card_name.replace(' ', '_').replace('/', '_').replace(':', '_')
        dest_path = images_dir / f"{safe_name}.jpg"
        
        with open(dest_path, 'wb') as f:
            f.write(img_response.content)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error for {card_name}: {e}")
        return False

def main():
    global images_dir
    
    # Configuration
    base_dir = Path('/home/dgetty/repos/MTG_Draft_Guide')
    html_file = base_dir / 'html_json' / 'strixhaven-draft-guide.html'
    images_dir = base_dir / 'images' / 'cards'
    
    # Create output directory
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract card names from HTML
    print("📖 Reading HTML file...")
    card_names = extract_cards_from_html(html_file)
    print(f"   Found {len(card_names)} unique cards\n")
    
    # Download images with rate limiting (Scryfall: 1 req/sec recommended)
    print("📥 Downloading images...\n")
    success_count = 0
    failed_cards = []
    
    for i, card_name in enumerate(card_names, 1):
        status = f"[{i}/{len(card_names)}] {card_name}"
        print(f"   {status}", end="\r")
        
        if download_card_image(card_name):
            success_count += 1
        else:
            failed_cards.append(card_name)
        
        # Rate limiting - stay under Scryfall's limit
        time.sleep(1.0)
    
    print(f"\r   ✓ Download complete!                    ")
    print(f"\n✅ Results:")
    print(f"   Success: {success_count}/{len(card_names)} cards")
    if failed_cards:
        print(f"   Failed:  {len(failed_cards)} cards")
        for card in failed_cards[:10]:
            print(f"      - {card}")
        if len(failed_cards) > 10:
            print(f"      ... and {len(failed_cards) - 10} more")
    
    # Summary
    total_size = sum(
        f.stat().st_size 
        for f in images_dir.glob('*.jpg')
    )
    print(f"\n📁 Images saved to: {images_dir}")
    print(f"   Total size: {total_size / 1024:.1f} KB")

if __name__ == '__main__':
    main()
