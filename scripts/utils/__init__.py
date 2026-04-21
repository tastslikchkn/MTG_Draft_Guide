"""
Shared utilities for MTG Draft Guide scripts.
Provides common functions and constants used across multiple modules.

This is the main entry point - imports everything from submodules for easy access:
    from scripts.utils import fetch_card_by_name, get_color_group, slugify
"""

import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass  # python-dotenv not installed, use system env vars only

import re
from typing import Optional, Dict, Any, List


# ============================================================================
# API CONFIGURATION
# ============================================================================

# Load from environment variables (set in .env or system)
JUSTTCG_API_KEY = os.getenv('JUSTTCG_API_KEY', '')
JUSTTCG_GAME_ID = os.getenv('JUSTTCG_GAME_ID', 'magic-the-gathering')


# ============================================================================
# IMPORTS FROM SUBMODULES
# ============================================================================
# Import everything from submodules so users can access via scripts.utils.*

from .api import (
    # HTTP client
    make_request,
    
    # Scryfall API
    fetch_card_by_name,
    fetch_card_image_url,
    download_card_image,
    search_cards,
    batch_download_images,
    
    # JustTCG API  
    fetch_card_by_name_justtcg,
    extract_price_data as api_extract_price_data,
)

from .card_data import (
    # String utilities
    sanitize_filename,
    slugify,
    title_case_from_slug,
    clean_card_name,
    
    # HTML parsers
    CardNameExtractor,
    extract_card_names_from_html,
    extract_card_names_from_alt_attributes,
    
    # Data model
    CardData,
    
    # File operations
    load_card_cache,
    save_card_cache,
    get_cached_image_paths,
)

from .color_rarity import (
    # Constants
    COLOR_NAMES,
    COLOR_GROUP_DISPLAY,
    COLOR_GROUP_ORDER,
    COLOR_CSS_CLASSES,
    COLOR_SECTIONS,
    
    RARITY_ORDER,
    RARITY_LETTERS,
    RARITY_COLORS,
    RARITY_INFO,
    
    # Color group functions
    get_color_group,
    get_color_group_for_card,
    
    # Rarity functions
    get_rarity_from_string,
    get_rarity_letter,
    get_rarity_color,
    get_rarity_sort_key,
    
    # Sorting/grouping helpers
    sort_cards_by_color_then_rarity,
    group_cards_by_color,
    group_cards_by_rarity,
)

from .html_templates import (
    # Template functions
    get_gallery_html_template,
    generate_rarity_legend_html,
    generate_card_item_html,
    generate_card_grid_html,
    generate_rarity_group_html,
    generate_color_section_html,
    generate_full_gallery_html,
    save_gallery_html,
)


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# Kept for backward compatibility with existing scripts
# ============================================================================

def get_color_group_display_name(group: str) -> str:
    """Legacy: Get display name for a color group."""
    return COLOR_GROUP_DISPLAY.get(group, group.replace('_', ' ').title())


def get_rarity_order(rarity: str) -> int:
    """Legacy: Return sort order for rarity (M=0, R=1, U=2, C=3)."""
    return get_rarity_sort_key(rarity)


def get_color_group_order(group: str) -> int:
    """Legacy: Return sort order for color groups."""
    return COLOR_GROUP_ORDER.index(group) if group in COLOR_GROUP_ORDER else 99


def get_avg_price_7d(card_data: Dict) -> Optional[float]:
    """Extract avg_price_7d from card prices data."""
    prices = card_data.get('prices', {})
    if not prices or 'prices' not in prices:
        return None
    
    # Try near_mint_normal first, then near_mint_foil
    for key in ['near_mint_normal', 'near_mint_foil']:
        price_data = prices['prices'].get(key, {})
        avg_price = price_data.get('avg_price_7d')
        if avg_price is not None:
            return avg_price
    
    # Fallback to any available price
    for key, price_data in prices['prices'].items():
        avg_price = price_data.get('avg_price_7d')
        if avg_price is not None:
            return avg_price
    
    return None


def format_price(price: Optional[float]) -> str:
    """Format price as currency string."""
    if price is None:
        return "No data"
    return f"${price:.2f}"


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


# ============================================================================
# HTML TEMPLATE UTILITIES (LEGACY)
# Kept for backward compatibility
# ============================================================================

def get_card_gallery_css() -> str:
    """Legacy: Return the CSS styles for card gallery pages."""
    return '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 40px 20px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            color: #a0a0a0;
            font-size: 1.1rem;
        }
        
        .legend {
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 20px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: white;
            font-size: 0.9rem;
        }
        
        .legend-rarity {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
        }
        
        .color-section {
            margin-bottom: 40px;
            padding: 20px;
            border-radius: 12px;
        }
        
        .color-title {
            font-size: 1.5rem;
            color: white;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,255,255,0.2);
        }
        
        .rarity-group {
            margin-bottom: 25px;
        }
        
        .rarity-title {
            font-size: 1rem;
            color: #a0a0a0;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .rarity-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
        
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(345px, 1fr));
            gap: 30px;
        }
        
        .card-item {
            background: #fff;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card-item:hover {
            transform: translateY(-9px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        }
        
        .card-image-container {
            position: relative;
            padding-top: 157%;
            background: #f0f0f0;
        }
        
        .card-image {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .card-info {
            padding: 20px;
            text-align: center;
        }
        
        .card-name {
            font-size: 1.85rem;
            color: #333;
            margin-bottom: 9px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .card-mana-cost {
            font-size: 1.95rem;
            color: #666;
        }
        
        .card-price {
            font-size: 1.85rem;
            color: #2ECC40;
            font-weight: 500;
            margin-top: 6px;
        }
        
        @media (max-width: 768px) {
            .card-grid {
                grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
                gap: 20px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
        }
    '''


def get_card_gallery_html_header(
    title: str = "🎓 Strixhaven Card Gallery",
    subtitle: str = "Cards grouped by color, then rarity (M → R → U → C)"
) -> str:
    """Legacy: Generate the HTML header for card gallery pages."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{get_card_gallery_css()}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    
    <div class="legend">
        <div class="legend-item"><span class="legend-rarity" style="background: #FFD700;"></span> Mythic Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #C41E3A;"></span> Rare</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #228B22;"></span> Uncommon</div>
        <div class="legend-item"><span class="legend-rarity" style="background: #696969;"></span> Common</div>
    </div>

'''


def get_card_gallery_html_footer() -> str:
    """Legacy: Generate the HTML footer for card gallery pages."""
    return '''
</body>
</html>
'''
