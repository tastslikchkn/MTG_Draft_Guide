#!/usr/bin/env python3
"""
Fetch All Secrets of Strixhaven Cards with Prices from JustTCG API.
Uses Scryfall to get card list, then JustTCG for prices.

Refactored to use centralized utility modules.
"""

import time
from pathlib import Path

# Import utilities from centralized modules
from scripts.utils.api import search_cards, fetch_card_by_name_justtcg
from scripts.utils import extract_price_data as api_extract_price_data


def main():
    output_file = Path("./justtcg_sos_cards.json")
    
    print(f"📚 Fetching SOS Cards with JustTCG Prices")
    print(f"=" * 50)
    
    # Step 1: Get all SOS card names from Scryfall using centralized utility
    print(f"\n⬇️  Step 1: Fetching SOS card list from Scryfall...")
    result = search_cards("e:sos order:set", unique="cards")
    card_names = [card['name'] for card in result.get('data', [])]
    
    if not card_names:
        print("❌ Failed to fetch card names from Scryfall")
        return
    
    print(f"   Found {len(card_names)} cards in SOS set")
    
    # Step 2: Fetch prices from JustTCG for each card using centralized utility
    print(f"\n⬇️  Step 2: Fetching prices from JustTCG...")
    print("-" * 50)
    
    cards_with_prices = {}
    cards_without_prices = []
    
    for i, card_name in enumerate(card_names, 1):
        print(f"[{i}/{len(card_names)}] {card_name}", end="")
        
        # Use centralized JustTCG fetch utility
        api_response = fetch_card_by_name_justtcg(card_name)
        price_data = api_extract_price_data(api_response)
        
        if price_data:
            cards_with_prices[card_name] = price_data
            print(" ✓")
        else:
            cards_without_prices.append(card_name)
            print(" ✗")
        
        # Rate limiting (0.5s for JustTCG)
        time.sleep(0.5)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(cards_with_prices, f, indent=2, ensure_ascii=False)
    
    # Summary
    print(f"\n" + "=" * 50)
    print(f"📊 FETCH COMPLETE")
    print(f"   Total SOS cards:      {len(card_names)}")
    print(f"   With JustTCG prices:  {len(cards_with_prices)}")
    print(f"   Without prices:       {len(cards_without_prices)}")
    
    if cards_without_prices and len(cards_without_prices) <= 10:
        print(f"\n❌ Cards without price data:")
        for card in cards_without_prices:
            print(f"   - {card}")
    
    file_size = output_file.stat().st_size
    print(f"\n💾 Output file size: {file_size / 1024:.2f} KB")
    print(f"   Saved to: {output_file.absolute()}")


if __name__ == "__main__":
    main()
