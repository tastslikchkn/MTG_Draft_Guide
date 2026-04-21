"""
HTML templates and generation utilities for card galleries.
Centralized HTML generation to avoid duplication across gallery scripts.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path


def get_gallery_html_template() -> str:
    """
    Get the base HTML template for card galleries.
    
    Returns:
        Complete HTML string with CSS styling
    """
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strixhaven Card Gallery</title>
    <style>
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
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 12px;
        }
        
        .card-item {
            background: #fff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card-item:hover {
            transform: translateY(-4px);
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
            padding: 8px;
            text-align: center;
        }
        
        .card-name {
            font-size: 0.75rem;
            color: #333;
            margin-bottom: 4px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .card-mana-cost {
            font-size: 0.8rem;
            color: #666;
        }
        
        .rarity-badge {
            position: absolute;
            top: 5px;
            right: 5px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: bold;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        @media (max-width: 768px) {
            .card-grid {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 8px;
            }
            
            .header h1 {
                font-size: 1.8rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Strixhaven Card Gallery</h1>
        <p>{subtitle}</p>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <span class="legend-rarity" style="background: #FFD700;"></span>
            <span>Mythic</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #C41E3A;"></span>
            <span>Rare</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #228B22;"></span>
            <span>Uncommon</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #696969;"></span>
            <span>Common</span>
        </div>
    </div>
    
    {content}
</body>
</html>
'''


def generate_rarity_legend_html() -> str:
    """
    Generate HTML for rarity legend.
    
    Returns:
        HTML string for rarity legend div
    """
    return '''
    <div class="legend">
        <div class="legend-item">
            <span class="legend-rarity" style="background: #FFD700;"></span>
            <span>Mythic</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #C41E3A;"></span>
            <span>Rare</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #228B22;"></span>
            <span>Uncommon</span>
        </div>
        <div class="legend-item">
            <span class="legend-rarity" style="background: #696969;"></span>
            <span>Common</span>
        </div>
    </div>
'''


def generate_card_item_html(
    card: Dict[str, Any],
    show_rarity_badge: bool = True,
    show_price: bool = False
) -> str:
    """
    Generate HTML for a single card item.
    
    Args:
        card: Card data dictionary with name, image_path, etc.
        show_rarity_badge: Whether to show rarity letter badge
        show_price: Whether to show price info
        
    Returns:
        HTML string for one card item div
    """
    from .color_rarity import (
        get_rarity_letter,
        get_rarity_color,
        get_avg_price_7d,
        format_price
    )
    
    name = card.get('name', 'Unknown Card')
    image_path = card.get('image_path', '')
    mana_cost = card.get('mana_cost', '')
    rarity = card.get('rarity', 'common')
    
    # Generate rarity badge
    rarity_letter = get_rarity_letter(rarity)
    rarity_color = get_rarity_color(rarity)
    
    rarity_badge_html = ''
    if show_rarity_badge and rarity_letter in ['M', 'R', 'U']:
        rarity_badge_html = f'''<div class="rarity-badge" style="background: {rarity_color};">
            {rarity_letter}
        </div>'''
    
    # Generate price HTML
    price_html = ''
    if show_price:
        avg_price = get_avg_price_7d(card.get('prices'))
        if avg_price:
            price_html = f'<div class="card-price">${avg_price:.2f}</div>'
    
    # Build card HTML
    html = f'''
        <div class="card-item">
            <div class="card-image-container">
                {rarity_badge_html}
                {'<img src="' + image_path + '" class="card-image" alt="' + name + '">' if image_path else '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#999;font-size:2rem;">?</div>'}
            </div>
            <div class="card-info">
                <div class="card-name">{name}</div>
                {f'<div class="card-mana-cost">{mana_cost}</div>' if mana_cost else ''}
                {price_html}
            </div>
        </div>
'''
    
    return html


def generate_card_grid_html(
    cards: List[Dict[str, Any]],
    show_rarity_badge: bool = True,
    show_price: bool = False
) -> str:
    """
    Generate HTML for a grid of card items.
    
    Args:
        cards: List of card data dictionaries
        show_rarity_badge: Whether to show rarity badges
        show_price: Whether to show prices
        
    Returns:
        HTML string for card-grid div with all cards
    """
    cards_html = ''.join(
        generate_card_item_html(card, show_rarity_badge, show_price)
        for card in cards
    )
    
    return f'<div class="card-grid">{cards_html}</div>'


def generate_rarity_group_html(
    rarity: str,
    cards: List[Dict[str, Any]],
    show_price: bool = False
) -> str:
    """
    Generate HTML for a rarity group section.
    
    Args:
        rarity: Rarity name ('mythic', 'rare', etc.)
        cards: List of cards in this rarity
        show_price: Whether to show prices
        
    Returns:
        HTML string for rarity-group div
    """
    from .color_rarity import get_rarity_letter, get_rarity_color
    
    if not cards:
        return ''
    
    letter = get_rarity_letter(rarity)
    color = get_rarity_color(rarity)
    display_name = rarity.capitalize()
    
    return f'''
    <div class="rarity-group">
        <div class="rarity-title">
            <span class="rarity-dot" style="background: {color};"></span>
            <span>{display_name} ({len(cards)})</span>
        </div>
        {generate_card_grid_html(cards, show_price=show_price)}
    </div>
'''


def generate_color_section_html(
    color_group: str,
    cards: List[Dict[str, Any]],
    title: Optional[str] = None,
    background_color: Optional[str] = None,
    show_price: bool = False
) -> str:
    """
    Generate HTML for a complete color section.
    
    Args:
        color_group: Color group identifier (mono_white, multicolor, etc.)
        cards: List of cards in this color group
        title: Custom title (defaults to COLOR_SECTIONS)
        background_color: Custom background (defaults to COLOR_SECTIONS)
        show_price: Whether to show prices
        
    Returns:
        HTML string for color-section div
    """
    from .color_rarity import COLOR_SECTIONS, group_cards_by_rarity
    
    if not cards:
        return ''
    
    section_info = COLOR_SECTIONS.get(color_group, (color_group.title(), '#f0f0f0'))
    section_title = title or section_info[0]
    section_bg = background_color or section_info[1]
    
    # Group by rarity
    by_rarity = group_cards_by_rarity(cards)
    
    # Generate rarity groups HTML
    rarity_html = ''
    for rarity in ['mythic', 'rare', 'uncommon', 'common']:
        rarity_html += generate_rarity_group_html(rarity, by_rarity[rarity], show_price)
    
    return f'''
    <div class="color-section" style="background: {section_bg};">
        <h2 class="color-title">{section_title} ({len(cards)} cards)</h2>
        {rarity_html}
    </div>
'''


def generate_full_gallery_html(
    card_cache: Dict[str, Any],
    subtitle: str = "A visual guide to Strixhaven commons and uncommons",
    group_by: str = "color",  # 'color' or 'rarity'
    show_price: bool = False
) -> str:
    """
    Generate complete gallery HTML from card cache.
    
    Args:
        card_cache: Dictionary of card data keyed by name
        subtitle: Subtitle text for header
        group_by: Grouping method ('color' or 'rarity')
        show_price: Whether to display prices
        
    Returns:
        Complete HTML string ready to save to file
    """
    from .color_rarity import (
        COLOR_GROUP_ORDER, 
        COLOR_SECTIONS,
        group_cards_by_color
    )
    
    # Convert card_cache values to list
    cards = list(card_cache.values())
    
    # Get base template
    template = get_gallery_html_template()
    
    if group_by == "color":
        # Group by color
        groups = group_cards_by_color(cards)
        
        content_html = ''
        for color_group in COLOR_GROUP_ORDER:
            if color_group in groups and groups[color_group]:
                section_info = COLOR_SECTIONS.get(color_group, (color_group.title(), '#f0f0f0'))
                content_html += generate_color_section_html(
                    color_group,
                    groups[color_group],
                    title=section_info[0],
                    background_color=section_info[1],
                    show_price=show_price
                )
    else:
        # Group by rarity - simpler layout
        from .color_rarity import group_cards_by_rarity
        by_rarity = group_cards_by_rarity(cards)
        
        content_html = '<div class="color-section" style="background: #1e1e3e;">'
        for rarity in ['mythic', 'rare', 'uncommon', 'common']:
            content_html += generate_rarity_group_html(rarity, by_rarity[rarity], show_price)
        content_html += '</div>'
    
    # Fill template
    html = template.format(
        subtitle=subtitle,
        content=content_html
    )
    
    return html


def save_gallery_html(html: str, output_path: Path) -> None:
    """
    Save generated HTML to file.
    
    Args:
        html: HTML string to save
        output_path: Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
