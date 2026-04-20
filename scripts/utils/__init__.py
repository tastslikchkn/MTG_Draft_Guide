"""
Shared utilities for MTG Draft Guide scripts.
Provides common functions and constants used across multiple modules.
"""

import re
from typing import Optional, Dict, Any, List


# ============================================================================
# API CONFIGURATION
# ============================================================================

JUSTTCG_API_KEY = "tcg_d8eb7084d5714807933f1690b2ed55b9"
JUSTTCG_GAME_ID = "magic-the-gathering"


# ============================================================================
# STRING UTILITIES
# ============================================================================

def slugify(name: str) -> str:
    """Convert card name to URL-safe filename.
    
    Args:
        name: The card name to convert
        
    Returns:
        A URL-safe slug with spaces replaced by hyphens, special characters removed,
        and converted to lowercase.
        
    Example:
        >>> slugify("Elite Interceptor // Rejoinder")
        'elite-interceptor--rejoinder'
    """
    # Replace spaces with hyphens
    slug = name.replace(' ', '-')
    # Remove special characters except hyphens and underscores
    slug = re.sub(r'[^a-zA-Z0-9\-_]', '', slug)
    # Convert to lowercase
    slug = slug.lower()
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug


def title_case_from_slug(slug: str) -> str:
    """Convert a slug back to title case.
    
    Args:
        slug: The URL-safe slug
        
    Returns:
        Title-cased string with hyphens replaced by spaces
    """
    return slug.replace('-', ' ').title()


# ============================================================================
# CARD COLOR UTILITIES
# ============================================================================

def get_color_group(colors: List[str]) -> str:
    """Determine the color group for a card based on its colors.
    
    Args:
        colors: List of color codes (e.g., ['W', 'U'] or [])
        
    Returns:
        Color group string: 'mono_white', 'mono_blue', 'mono_black', 
        'mono_red', 'mono_green', 'multicolor', or 'colorless'
        
    Examples:
        >>> get_color_group(['W'])
        'mono_white'
        >>> get_color_group(['W', 'U'])
        'multicolor'
        >>> get_color_group([])
        'colorless'
    """
    if not colors or len(colors) == 0:
        return "colorless"
    
    unique_colors = set(colors)
    num_colors = len(unique_colors)
    
    # Mono-color cards
    if num_colors == 1:
        color = list(unique_colors)[0]
        color_names = {
            'W': 'mono_white',
            'U': 'mono_blue', 
            'B': 'mono_black',
            'R': 'mono_red',
            'G': 'mono_green'
        }
        return color_names.get(color, 'multicolor')
    
    # Multi-color cards (2+ colors)
    if num_colors >= 2:
        return "multicolor"
    
    return "colorless"


def get_color_group_display_name(group: str) -> str:
    """Get display name for a color group.
    
    Args:
        group: The color group identifier
        
    Returns:
        Human-readable display name
    """
    names = {
        'mono_white': 'White Cards',
        'mono_blue': 'Blue Cards',
        'mono_black': 'Black Cards',
        'mono_red': 'Red Cards',
        'mono_green': 'Green Cards',
        'multicolor': 'Multi-Color Cards',
        'colorless': 'Colorless Cards',
        'lands': 'Lands'
    }
    return names.get(group, group.replace('_', ' ').title())


# ============================================================================
# RARITY UTILITIES
# ============================================================================

def get_rarity_order(rarity: str) -> int:
    """Return sort order for rarity (M=0, R=1, U=2, C=3).
    
    Args:
        rarity: Rarity string (e.g., 'mythic', 'rare', 'uncommon', 'common')
        
    Returns:
        Integer sort order (lower = higher rarity)
    """
    rarity_map = {
        'mythic': 0,
        'rare': 1,
        'uncommon': 2,
        'common': 3
    }
    return rarity_map.get(rarity.lower() if rarity else '', 4)


def get_rarity_letter(rarity: str) -> str:
    """Convert full rarity name to single letter.
    
    Args:
        rarity: Full rarity name
        
    Returns:
        Single letter: 'M', 'R', 'U', or 'C'
    """
    if not rarity:
        return 'C'
    
    rarity_lower = rarity.lower()
    if 'mythic' in rarity_lower:
        return 'M'
    elif 'rare' in rarity_lower:
        return 'R'
    elif 'uncommon' in rarity_lower:
        return 'U'
    else:
        return 'C'


def get_color_group_order(group: str) -> int:
    """Return sort order for color groups.
    
    Args:
        group: Color group identifier
        
    Returns:
        Integer sort order for display purposes
    """
    order = {
        'mono_white': 0,
        'mono_blue': 1,
        'mono_black': 2,
        'mono_red': 3,
        'mono_green': 4,
        'multicolor': 5,
        'colorless': 6,
        'lands': 7
    }
    return order.get(group, 99)


# ============================================================================
# PRICE DATA UTILITIES
# ============================================================================

def extract_price_data(api_response: Optional[Dict]) -> Optional[Dict[str, Any]]:
    """Extract price data from JustTCG API response.
    
    Args:
        api_response: Raw JSON response from JustTCG API
        
    Returns:
        Dictionary containing extracted price information, or None if no data found
    """
    if not api_response or 'data' not in api_response or len(api_response['data']) == 0:
        return None
    
    product = api_response['data'][0]
    
    # Skip sealed products
    if product.get('number') == 'N/A':
        return None
    
    variants = product.get('variants', [])
    prices = {}
    
    for variant in variants:
        condition = variant.get('condition', 'Unknown')
        printing = variant.get('printing', 'Normal')
        price = variant.get('price')
        
        if price is not None:
            key = f"{condition}_{printing}".lower().replace(' ', '_')
            prices[key] = {
                'price': price,
                'condition': condition,
                'printing': printing,
                'last_updated': variant.get('lastUpdated'),
                'avg_price_7d': variant.get('avgPrice'),
                'min_price_7d': variant.get('minPrice7d'),
                'max_price_7d': variant.get('maxPrice7d')
            }
    
    if not prices:
        return None
    
    return {
        'justtcg_id': product.get('id'),
        'set_name': product.get('set_name', ''),
        'set_number': product.get('number'),
        'rarity': product.get('rarity', ''),
        'scryfall_id': product.get('scryfallId'),
        'tcgplayer_id': product.get('tcgplayerId'),
        'prices': prices,
        'url': f"https://www.justtcg.com/product/{product.get('id')}" if product.get('id') else None
    }


def get_avg_price_7d(card_data: Dict) -> Optional[float]:
    """Extract avg_price_7d from card prices data.
    
    Args:
        card_data: Card data dictionary containing prices
        
    Returns:
        Average 7-day price as float, or None if not available
    """
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
    """Format price as currency string.
    
    Args:
        price: Price value or None
        
    Returns:
        Formatted currency string (e.g., "$12.34" or "No data")
    """
    if price is None:
        return "No data"
    return f"${price:.2f}"


# ============================================================================
# HTML TEMPLATE UTILITIES
# ============================================================================

def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple.
    
    Args:
        hex_color: Hex color string (e.g., '#FFD700')
        
    Returns:
        RGB tuple (e.g., (255, 215, 0))
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_card_gallery_css() -> str:
    """Return the CSS styles for card gallery pages.
    
    Returns:
        Complete CSS string for card gallery styling
    """
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
            padding-top: 157%; /* Card aspect ratio ~1.57 */
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


def get_card_gallery_html_header(title: str = "🎓 Strixhaven Card Gallery", 
                                  subtitle: str = "Cards grouped by color, then rarity (M → R → U → C)") -> str:
    """Generate the HTML header for card gallery pages.
    
    Args:
        title: Page title
        subtitle: Subtitle text
        
    Returns:
        Complete HTML from <!DOCTYPE> through opening of body content
    """
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
    """Generate the HTML footer for card gallery pages.
    
    Returns:
        Closing HTML tags
    """
    return '''
</body>
</html>
'''


# ============================================================================
# COLOR SECTION CONFIGURATION
# ============================================================================

COLOR_SECTIONS = [
    ('mono_white', 'White Cards', '#ffffff'),
    ('mono_blue', 'Blue Cards', '#0074D9'),
    ('mono_black', 'Black Cards', '#111111'),
    ('mono_red', 'Red Cards', '#FF4136'),
    ('mono_green', 'Green Cards', '#2ECC40'),
    ('multicolor', 'Multi-Color Cards', '#B10DC9'),
    ('colorless', 'Colorless Cards', '#AAAAAA'),
    ('lands', 'Lands', '#FF851B'),
]


RARITY_INFO = {
    'M': ('Mythic Rare (M)', '#FFD700'),
    'R': ('Rare (R)', '#C41E3A'),
    'U': ('Uncommon (U)', '#228B22'),
    'C': ('Common (C)', '#696969')
}