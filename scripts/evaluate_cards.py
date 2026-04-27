#!/usr/bin/env python3
"""
Card Evaluation Script for MTG Draft Guide
==========================================

Calculates power levels and draft priority scores for all cards in a set,
then saves the evaluations back to the JSON cache file.

Usage:
    python evaluate_cards.py [--set-code sos] [--output path/to/output.json]
    
Examples:
    # Evaluate SOS cards (default)
    python evaluate_cards.py
    
    # Fetch fresh data from Scryfall and evaluate
    python evaluate_cards.py --fetch-fresh
    
    # Evaluate with custom output
    python evaluate_cards.py --output evaluated_sos_cards.json
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    calculate_power_level,
    get_power_level_tier,
    calculate_draft_priority_score,
    add_card_evaluations,
    add_value_evaluations,  # NEW: value-based evaluation
    add_combo_evaluations,  # NEW: combo detection
    load_card_cache,
    save_card_cache,
    fetch_set_cards,
)


def print_evaluation_summary(cards: List[Dict[str, Any]]) -> None:
    """
    Print a summary of card evaluations.
    
    Args:
        cards: List of evaluated card dictionaries
    """
    # Filter out cards with no power level (missing data)
    valid_cards = [c for c in cards if c.get('power_level') is not None]
    
    if not valid_cards:
        print("\n⚠ No cards could be evaluated - missing power/toughness data.")
        print("   Use --fetch-fresh to download complete card data from Scryfall.")
        return
    
    # Group by tier
    tiers = {'S+': [], 'S': [], 'A+': [], 'A': [], 'B+': [], 'B': [], 'C': [], 'D': []}
    for card in valid_cards:
        tier = card.get('tier', 'B')
        if tier in tiers:
            tiers[tier].append(card)
    
    print("\n" + "=" * 60)
    print("CARD EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total cards evaluated: {len(valid_cards)} / {len(cards)}")
    print()
    
    # Print tier distribution
    print("Tier Distribution:")
    print("-" * 40)
    for tier in ['S+', 'S', 'A+', 'A', 'B+', 'B', 'C', 'D']:
        count = len(tiers[tier])
        percentage = (count / len(valid_cards)) * 100 if valid_cards else 0
        bar = "█" * int(percentage // 2)
        print(f"  {tier:3} | {count:3} ({percentage:5.1f}%) {bar}")
    
    # Print top cards by draft score
    sorted_cards = sorted(valid_cards, key=lambda c: c.get('draft_score', 0), reverse=True)
    print("\nTop 10 Cards by Draft Priority:")
    print("-" * 60)
    for i, card in enumerate(sorted_cards[:10], 1):
        name = card.get('name', 'Unknown')
        score = card.get('draft_score', 0)
        tier = card.get('tier', '?')
        power_level = card.get('power_level', 0)
        cmc = card.get('cmc', 0)
        print(f"{i:2}. [{tier}] {name:40} (Score: {score:3}, PL: {power_level:+.2f}, CMC: {cmc})")
    
    # Print top creatures by power level
    creatures = [c for c in valid_cards if 'creature' in c.get('type_line', '').lower() and c.get('power')]
    sorted_creatures = sorted(creatures, key=lambda c: c.get('power_level', 0), reverse=True)
    print("\nTop 10 Creatures by Power Level:")
    print("-" * 60)
    for i, card in enumerate(sorted_creatures[:10], 1):
        name = card.get('name', 'Unknown')
        power_level = card.get('power_level', 0)
        cmc = card.get('cmc', 0)
        pt = f"{card.get('power', '?')}/{card.get('toughness', '?')}"
        keywords = ', '.join(card.get('detected_keywords', [])[:3])
        if keywords:
            print(f"{i:2}. {name:35} ({pt}, CMC {cmc}): PL={power_level:+.2f} [{keywords}]")
        else:
            print(f"{i:2}. {name:35} ({pt}, CMC {cmc}): PL={power_level:+.2f}")


def fetch_fresh_card_data(set_code: str = 'sos', verbose: bool = True) -> List[Dict[str, Any]]:
    """
    Fetch fresh card data from Scryfall API with full fields including power/toughness.
    
    Args:
        set_code: Set code (e.g., 'sos' for Secrets of Strixhaven)
        verbose: Whether to print progress
        
    Returns:
        List of complete card dictionaries
    """
    if verbose:
        print(f"Fetching fresh card data from Scryfall for set: {set_code.upper()}")
    
    result = fetch_set_cards(set_code, unique='cards')
    cards = result.get('data', [])
    
    if verbose:
        print(f"Fetched {len(cards)} cards from Scryfall")
    
    return cards



def evaluate_cards(
    cards: List[Dict[str, Any]],
    output_path: Optional[Path] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Evaluate a list of cards and optionally save to file.
    
    Pipeline:
        1. add_card_evaluations - power level & draft score
        2. add_value_evaluations - value classification (bombs, hidden gems)
        3. add_combo_evaluations - synergy detection
    
    Args:
        cards: List of card dictionaries
        output_path: Optional path to save evaluated cards
        verbose: Whether to print summary
        
    Returns:
        Dictionary with evaluation results:
            - cards: Evaluated card list
            - total_cards: Number of cards processed
            - tier_distribution: Count per tier
            - top_cards: Top 10 by draft score
    """
    if verbose:
        print(f"Evaluating {len(cards)} cards...")
    
    # Step 1: Add basic evaluations (power level, draft score)
    evaluated_cards = add_card_evaluations(cards)
    
    # Step 2: Add value-based evaluations (bombs, hidden gems)
    evaluated_cards = add_value_evaluations(evaluated_cards)
    
    # Step 3: Detect combos between cards
    evaluated_cards = add_combo_evaluations(evaluated_cards)
    
    # Calculate tier distribution (only valid cards)
    valid_cards = [c for c in evaluated_cards if c.get('power_level') is not None]
    tier_distribution = {'S+': 0, 'S': 0, 'A+': 0, 'A': 0, 'B+': 0, 'B': 0, 'C': 0, 'D': 0}
    for card in valid_cards:
        tier = card.get('tier', 'B')
        tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
    
    # Get top cards by draft score
    sorted_cards = sorted(valid_cards, key=lambda c: c.get('draft_score', 0), reverse=True)
    top_cards = sorted_cards[:10]
    
    # Save to output file if specified
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(evaluated_cards, f, indent=2, ensure_ascii=False)
        
        if verbose:
            print(f"Saved evaluations to: {output_path}")
    
    if verbose:
        print_evaluation_summary(evaluated_cards)
    
    return {
        'cards': evaluated_cards,
        'total_cards': len(evaluated_cards),
        'valid_cards': len(valid_cards),
        'tier_distribution': tier_distribution,
        'top_cards': top_cards
    }


def main():
    """Main entry point for the evaluation script."""
    parser = argparse.ArgumentParser(
        description='Evaluate MTG cards and calculate power levels/draft scores.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Evaluate default card cache
  %(prog)s --fetch-fresh            # Fetch fresh data from Scryfall first
  %(prog)s -i custom.json           # Evaluate custom file
  %(prog)s -o output.json           # Save to specific output file
  %(prog)s -q                       # Quiet mode (no summary)
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=None,
        help='Input JSON file path (default: fetch from Scryfall)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=None,
        help='Output JSON file path (default: html_json/evaluated_{set_code}.json)'
    )
    
    parser.add_argument(
        '--set-code', '-s',
        type=str,
        default='sos',
        help='Set code for Scryfall fetch (default: sos)'
    )
    
    parser.add_argument(
        '--fetch-fresh',
        action='store_true',
        help='Fetch fresh card data from Scryfall API (includes power/toughness)'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - skip summary output'
    )
    
    args = parser.parse_args()
    
    # Set default output path based on set code if not specified
    if args.output is None:
        base_path = Path(__file__).parent.parent / 'html_json'
        args.output = base_path / f'evaluated_{args.set_code}.json'
    
    # Get card data
    cards = []
    if args.fetch_fresh:
        # Fetch fresh data from Scryfall
        cards = fetch_fresh_card_data(args.set_code, verbose=not args.quiet)
    elif args.input:
        # Load from input file
        if not args.input.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        
        if not args.quiet:
            print(f"Loading card cache from: {args.input}")
        
        with open(args.input, 'r', encoding='utf-8') as f:
            cards_dict = json.load(f)
        
        # Convert dict to list if needed
        if isinstance(cards_dict, dict):
            cards = list(cards_dict.values())
        else:
            cards = cards_dict
        
        if not args.quiet:
            print(f"Loaded {len(cards)} cards")
    else:
        # Default: fetch fresh
        if not args.quiet:
            print("No input specified, fetching fresh data from Scryfall...")
        cards = fetch_fresh_card_data(args.set_code, verbose=not args.quiet)
    
    # Run evaluation
    try:
        result = evaluate_cards(
            cards=cards,
            output_path=args.output,
            verbose=not args.quiet
        )
        
        valid_count = result.get('valid_cards', result['total_cards'])
        print(f"\n✓ Successfully evaluated {valid_count}/{result['total_cards']} cards")
        
        if valid_count < result['total_cards']:
            print("  ⚠ Some cards missing power/toughness data.")
            print("    Use --fetch-fresh to get complete card data from Scryfall.")
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error during evaluation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
