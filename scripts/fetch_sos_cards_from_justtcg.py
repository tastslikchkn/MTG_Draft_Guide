#!/usr/bin/env python3
"""
Fetch All Secrets of Strixhaven Cards with Prices from JustTCG API
Uses Scryfall to get card list, then JustTCG for prices.
"""

import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from scripts.utils import JUSTTCG_API_KEY, extract_price_data


def fetch_sos_card_names_from_scryfall():
    """Fetch all SOS card names from Scryfall API."""
    url = "https://api.scryfall.com/cards/search?q=e%3Asos+order%3Aset&unique=cards"
    
    req = urllib.request.Request(
        url,
        headers={
            'User-Agent': 'MTG_Draft_Guide/1.0 (by tastslikchkn)',
            'Accept': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return [card['name'] for card in data.get('data', [])]
    except Exception as e:
        print(f"✗ Error fetching from Scryfall: {e}")
        return []


def fetch_card_price_from_justtcg(card_name):
    """Fetch price data for a single card from JustTCG API."""
    url = f"https://api.justtcg.com/v1/cards?game=magic-the-gathering&q={urllib.parse.quote(card_name)}"
    
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
    except Exception:
        return None


def main():
    output_file = Path("./justtcg_sos_cards.json")
    
    print(f"📚 Fetching SOS Cards with JustTCG Prices")
    print(f"=" * 50)
    
    # Step 1: Get all SOS card names from Scryfall
    print(f"\n⬇️  Step 1: Fetching SOS card list from Scryfall...")
    card_names = fetch_sos_card_names_from_scryfall()
    
    if not card_names:
        print("❌ Failed to fetch card names from Scryfall")
        return
    
    print(f"   Found {len(card_names)} cards in SOS set")
    
    # Step 2: Fetch prices from JustTCG for each card
    print(f"\n⬇️  Step 2: Fetching prices from JustTCG...")
    print("-" * 50)
    
    cards_with_prices = {}
    cards_without_prices = []
    
    for i, card_name in enumerate(card_names, 1):
        print(f"[{i}/{len(card_names)}] {card_name}", end="")
        
        api_response = fetch_card_price_from_justtcg(card_name)
        price_data = extract_price_data(api_response)
        
        if price_data:
            cards_with_prices[card_name] = price_data
            print(" ✓")
        else:
            cards_without_prices.append(card_name)
            print(" ✗")
        
        # Rate limiting
        time.sleep(0.5)
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
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
    import urllib.parse
    main()