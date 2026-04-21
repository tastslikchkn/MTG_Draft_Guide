#!/usr/bin/env python3
"""
Card Price Fetcher for Strixhaven Draft Guide
Fetches price data from JustTCG API and merges with existing card cache.

Refactored to use centralized utility modules.
"""

import json
import time
from pathlib import Path

# Import utilities from centralized modules
from scripts.utils import (
    fetch_card_by_name_justtcg,
    extract_price_data as api_extract_price_data,
    load_card_cache,
    save_card_cache,
)


def main():
    # Configuration
    cache_file = Path("./strixhaven_card_cache.json")
    
    print(f"📚 Strixhaven Draft Guide - Card Price Fetcher (JustTCG)")
    print(f"=" * 50)
    
    # Load existing card cache using utility
    try:
        card_cache = load_card_cache(cache_file)
    except FileNotFoundError:
        print(f"❌ Error: {cache_file} not found! Run fetch_card_text_data.py first.")
        return
    
    card_names = list(card_cache.keys())
    
    # TEST MODE: Only process first 3 cards (per .clinerules/APIs.md)
    TEST_MODE = False
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
        
        # Use centralized JustTCG API client from utils.api
        api_response = fetch_card_by_name_justtcg(card_name)
        price_data = api_extract_price_data(api_response)
        
        if price_data:
            card_cache[card_name]['prices'] = price_data
            matched_count += 1
            print(f"    ✓ Fetched price data")
        else:
            failed_cards.append(card_name)
            print(f"    ✗ No price data found")
        
        # Rate limiting - wait between requests
        time.sleep(0.5)
    
    # Save updated cache using utility
    save_card_cache(card_cache, cache_file)
    
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
    main()
