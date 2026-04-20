#!/usr/bin/env python3
"""
Card Price Fetcher for Strixhaven Draft Guide
Fetches price data from JustTCG API and merges with existing card cache.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from scripts.utils import JUSTTCG_API_KEY, JUSTTCG_GAME_ID, extract_price_data


def fetch_card_by_name(card_name):
    """Fetch a single card by name from JustTCG API."""
    url = f"https://api.justtcg.com/v1/cards?game={JUSTTCG_GAME_ID}&q={urllib.parse.quote(card_name)}"
    
    req = urllib.request.Request(
        url,
        headers={
            'X-API-Key': JUSTTCG_API_KEY,
            'Accept': 'application/json',
            'User-Agent': 'MTG_Draft_Guide/1.0 (by tastslikchkn)'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return None
    except Exception as e:
            return None


def main():
    # Configuration
    cache_file = Path("./strixhaven_card_cache.json")
    
    print(f"📚 Strixhaven Draft Guide - Card Price Fetcher (JustTCG)")
    print(f"=" * 50)
    
    # Load existing card cache
    if not cache_file.exists():
        print(f"❌ Error: {cache_file} not found! Run fetch_card_text_data.py first.")
        return
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        card_cache = json.load(f)
    
    card_names = list(card_cache.keys())
    
    # TEST MODE: Only process first 3 cards (per .clinerules/APIs.md)
    TEST_MODE = False  # Disabled after successful test
    if TEST_MODE:
        card_names = card_names[:3]
        print(f"\n⚠️  TEST MODE - Fetching prices for only first 3 cards")
    
    print(f"\n📖 Found {len(card_cache)} cards in cache (fetching all)")
    
    # Fetch price data for each card with rate limiting
    print(f"\n⬇️  Starting API requests to JustTCG...")
    print("-" * 50)
    
    matched_count = 0
    failed_cards = []
    
    for i, card_name in enumerate(card_names, 1):
        print(f"[{i}/{len(card_names)}] {card_name}")
        
        api_response = fetch_card_by_name(card_name)
        price_data = extract_price_data(api_response)
        
        if price_data:
            # Merge price data into existing card entry
            card_cache[card_name]['prices'] = price_data
            matched_count += 1
            print(f"    ✓ Fetched price data")
        else:
            failed_cards.append(card_name)
            print(f"    ✗ No price data found")
        
        # Rate limiting - wait between requests
        time.sleep(0.5)
    
    # Save updated cache
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(card_cache, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 PRICE FETCH COMPLETE")
    print(f"   Total cards processed: {len(card_names)}")
    print(f"   Successfully matched:  {matched_count}")
    print(f"   No price found:       {len(failed_cards)}")
    
    if failed_cards and len(failed_cards) <= 10:
        print(f"\n❌ Cards without price data:")
        for card in failed_cards:
            print(f"   - {card}")
    
    # Calculate file size
    file_size = cache_file.stat().st_size
    print(f"\n💾 Updated cache file size: {file_size / 1024:.2f} KB")


if __name__ == "__main__":
    import urllib.parse
    main()