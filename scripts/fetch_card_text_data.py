#!/usr/bin/env python3
"""
Card Text Data Fetcher for Strixhaven Draft Guide
Reads downloaded card images and fetches text data from Scryfall API.
Saves results to strixhaven_card_cache.json
"""

import os
import time
import json
import urllib.request
import urllib.error
from pathlib import Path


def fetch_card_data(query_name):
    """Fetch card data from Scryfall API."""
    url = f"https://api.scryfall.com/cards/named?fuzzy={urllib.parse.quote(query_name)}"
    
    # Create request with proper headers (Scryfall requires User-Agent)
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'MTG_Draft_Guide/1.0 (by tastslikchkn)',
            'Accept': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"    ✗ Not found")
            return None
        else:
            print(f"    ✗ HTTP Error {e.code}")
            return None
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return None


def main():
    # Configuration
    images_dir = Path("./images/cards")
    output_file = Path("./strixhaven_card_cache.json")
    
    print(f"📚 Strixhaven Draft Guide - Card Text Data Fetcher")
    print(f"=" * 50)
    
    # Get all PNG files
    png_files = sorted(images_dir.glob("*.png"))
    
    # TEST MODE: Only fetch first 3 cards (per .clinerules/APIs.md)
    TEST_MODE = False  # Disabled after successful test
    if TEST_MODE:
        png_files = png_files[:3]
        print(f"\n⚠️  TEST MODE - Fetching only first 3 cards")
    
    print(f"\n📖 Found {len(png_files)} downloaded cards")
    print(f"   Output file: {output_file}")
    
    # Fetch data for each card with rate limiting
    print(f"\n⬇️  Starting API requests (1 req/sec for rate limiting)...")
    print("-" * 50)
    
    cache = {}
    failed_cards = []
    
    for i, png_file in enumerate(png_files, 1):
        filename = png_file.name
        display_name = filename.replace('.png', '').replace('-', ' ')
        query_name = display_name  # Use space-separated name for API
        
        print(f"[{i}/{len(png_files)}] {display_name}")
        
        data = fetch_card_data(query_name)
        
        if data:
            actual_name = data.get('name', display_name)
            cache[actual_name] = {
                'name': actual_name,
                'oracle_text': data.get('oracle_text', ''),
                'mana_cost': data.get('mana_cost', ''),
                'type_line': data.get('type_line', ''),
                'rarity': data.get('rarity', ''),
                'card_type': data.get('type_line', '').split(' — ')[0] if ' — ' in data.get('type_line', '') else data.get('type_line', ''),
                'colors': data.get('colors', []),
                'color_identity': data.get('color_identity', []),
                'cmc': data.get('cmc', 0),
                'set_name': data.get('set_name', ''),
                'artist': data.get('artist', ''),
                'flavor_text': data.get('flavor_text', ''),
                'image_uris': {
                    'normal': data.get('image_uris', {}).get('normal', ''),
                    'png': data.get('image_uris', {}).get('png', '')
                }
            }
            print(f"    ✓ Fetched text data")
        else:
            failed_cards.append(display_name)
        
        # Rate limiting - wait 1 second between requests (Scryfall limit)
        time.sleep(1.0)
    
    # Save to JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 FETCH COMPLETE")
    print(f"   Total cards:     {len(png_files)}")
    print(f"   Successfully:    {len(cache)}")
    print(f"   Failed:          {len(failed_cards)}")
    
    if failed_cards:
        print(f"\n❌ Failed cards:")
        for card in failed_cards:
            print(f"   - {card}")
    
    # Calculate file size
    file_size = output_file.stat().st_size
    print(f"\n💾 Cache file size: {file_size / 1024:.2f} KB")
    print(f"   Saved to: {output_file.absolute()}")


if __name__ == "__main__":
    import urllib.parse  # Import here to avoid issues
    main()