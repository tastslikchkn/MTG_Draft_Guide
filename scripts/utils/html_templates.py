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
        
        .value-badge {
            position: absolute;
            top: 5px;
            left: 5px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Tooltip Styles */
        .card-item[data-tooltip] {
            position: relative;
        }
        
        .card-item[data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: #fff;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.7rem;
            line-height: 1.4;
            max-width: 320px;
            width: max-content;
            max-height: 400px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
            margin-bottom: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        
        .card-item[data-tooltip]:hover::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 8px solid transparent;
            border-top-color: rgba(0, 0, 0, 0.95);
            margin-bottom: -16px;
            z-index: 999;
        }
        
        /* Combo Section Styles */
        .combo-section {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-top: 30px;
        }
        
        .combo-title {
            font-size: 1.3rem;
            color: #ffd700;
            margin-bottom: 15px;
            text-align: center;
        }
        
        .combo-grid {
            display: grid;
            gap: 15px;
        }
        
        .combo-group {
            background: rgba(0, 0, 0, 0.3);
            padding: 12px;
            border-radius: 8px;
        }
        
        .combo-item {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            margin-bottom: 8px;
            transition: transform 0.2s;
        }
        
        .combo-item:hover {
            transform: scale(1.02);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .combo-card-img {
            width: 40px;
            height: 63px;
            object-fit: cover;
            border-radius: 4px;
        }
        
        .combo-placeholder {
            width: 40px;
            height: 63px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            font-size: 1.5rem;
        }
        
        .combo-plus {
            color: #ffd700;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        .combo-text {
            flex: 1;
            color: #fff;
            font-size: 0.85rem;
            padding-left: 10px;
            border-left: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        /* Combo tooltip on hover */
        .combo-item[data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.95);
            color: #fff;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 0.75rem;
            max-width: 280px;
            z-index: 1000;
            margin-bottom: 8px;
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
    cmc = card.get('cmc', 0)
    power = card.get('power', '-')
    toughness = card.get('toughness', '-')
    oracle_text = card.get('oracle_text', '')
    
    # Value evaluation fields
    value_score = card.get('value_score', 0)
    value_category = card.get('value_category', 'MARGINAL')
    power_level = card.get('power_level', 0)
    is_bomb = card.get('is_bomb', False)
    bomb_reason = card.get('bomb_reason', '')
    combos = card.get('combos', [])  # List of combo dicts
    
    # Generate rarity badge
    rarity_letter = get_rarity_letter(rarity)
    rarity_color = get_rarity_color(rarity)
    
    rarity_badge_html = ''
    if show_rarity_badge and rarity_letter in ['M', 'R', 'U']:
        rarity_badge_html = f'''<div class="rarity-badge" style="background: {rarity_color};">
            {rarity_letter}
        </div>'''
    
    # Generate value category badge
    value_badges = {
        'BOMB': ('#ff4444', '💣'),
        'HIDDEN_GEM': ('#ffd700', '🔍'),
        'STAPLE': ('#4caf50', '📚'),
        'SOLID': ('#8bc34a', ''),
        'FAIR': ('#cddc39', ''),
        'FLOP': ('#e91e63', '⚠️'),
        'JUNK': ('#757575', '')
    }
    value_badge_html = ''
    if value_category in ['BOMB', 'HIDDEN_GEM', 'STAPLE']:
        badge_color, badge_icon = value_badges.get(value_category, ('#999', ''))
        value_badge_html = f'''<div class="value-badge" style="background: {badge_color};">
            {badge_icon}
        </div>'''
    
    # Generate price HTML
    price_html = ''
    if show_price:
        avg_price = get_avg_price_7d(card.get('prices'))
        if avg_price:
            price_html = f'<div class="card-price">${avg_price:.2f}</div>'
    
    # Generate tooltip content with value formula
    expected_max_by_rarity = {
        'common': 0.5,
        'uncommon': 1.2,
        'rare': 2.0,
        'mythic': 3.0
    }
    expected_max = expected_max_by_rarity.get(rarity.lower(), 0.5)
    
    # Build value formula tooltip
    pt_info = f"{power}/{toughness}" if power != '-' else ''
    keyword_bonus = card.get('keyword_bonus', 0)
    
    tooltip_content = f"Value Formula:<br>"
    tooltip_content += f"Power Level = ({pt_info}) - (2 × {cmc}) + Keywords({keyword_bonus:.2f})<br>"
    tooltip_content += f"         = {power_level:.2f}<br><br>"
    tooltip_content += f"Value Score = Power Level - Expected Max<br>"
    tooltip_content += f"           = {power_level:.2f} - ({rarity}: {expected_max})<br>"
    tooltip_content += f"           = <strong>{value_score:.2f}</strong><br><br>"
    
    if is_bomb:
        tooltip_content += f"<span style='color:#ff4444'>💣 BOMB: {bomb_reason.replace('_', ' ').title()}</span>"
    elif value_category == 'HIDDEN_GEM':
        tooltip_content += f"<span style='color:#ffd700'>🔍 HIDDEN GEM: Exceeds rarity expectations!</span>"
    
    # Add combo info to tooltip
    if combos:
        tooltip_content += "<br><br><strong>🔗 Combos:</strong><br>"
        for combo in combos[:3]:  # Show top 3 combos
            combo_text = combo.get('text', '')
            combo_cards = combo.get('with', [])
            if isinstance(combo_cards, list):
                combo_cards_str = ', '.join(str(c) for c in combo_cards[:2])
            else:
                combo_cards_str = str(combo_cards)
            tooltip_content += f"• <em>{combo_text}</em> with {combo_cards_str}<br>"
    
    # Build card HTML with data-tooltip attribute
    # Escape quotes in tooltip content for HTML attribute
    safe_tooltip = tooltip_content.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
    
    html = f'''
        <div class="card-item" data-value-score="{value_score}" data-value-category="{value_category}" data-tooltip="{safe_tooltip}">
            <div class="card-image-container">
                {rarity_badge_html}
                {value_badge_html}
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
    
    # Sort by value_score (descending) - highest value cards first!
    sorted_cards = sorted(cards, key=lambda c: c.get('value_score', 0), reverse=True)
    
    return f'''
    <div class="rarity-group">
        <div class="rarity-title">
            <span class="rarity-dot" style="background: {color};"></span>
            <span>{display_name} ({len(cards)}) - Sorted by Value</span>
        </div>
        {generate_card_grid_html(sorted_cards, show_price=show_price)}
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


def generate_combo_section_html(
    archetype_name: str,
    combos: list[dict],
    cards_data: dict[str, dict] = None
) -> str:
    """
    Generate HTML for a combo section at the bottom of an archetype.
    
    Args:
        archetype_name: Name of the archetype (e.g., 'Azorius Control')
        combos: List of combo dictionaries with keys:
            - 'card1': First card name
            - 'card2': Second card name  
            - 'text': Combo description
            - 'synergy_type': Type of synergy
        cards_data: Optional dict mapping card names to full card data (for images)
        
    Returns:
        HTML string for combo section div
    """
    if not combos:
        return ''
    
    # Group combos by synergy type
    from collections import defaultdict
    combos_by_type = defaultdict(list)
    for combo in combos:
        synergy_type = combo.get('synergy_type', 'general').replace('_', ' ').title()
        combos_by_type[synergy_type].append(combo)
    
    html_parts = [
        '<div class="combo-section">',
        f'    <h3 class="combo-title">🔗 {archetype_name} Combos</h3>',
        '    <div class="combo-grid">'
    ]
    
    for synergy_type, type_combos in combos_by_type.items():
        html_parts.append(f'        <div class="combo-group"><strong>{synergy_type}</strong>:')
        
        for combo in type_combos[:3]:  # Limit to top 3 per type
            card1 = combo.get('card1', '')
            card2 = combo.get('card2', '')
            text = combo.get('text', '')
            
            # Get images if available
            img1 = ''
            img2 = ''
            if cards_data:
                if card1 in cards_data and cards_data[card1].get('image_path'):
                    img1 = f'<img src="{cards_data[card1]["image_path"]}" class="combo-card-img">'
                if card2 in cards_data and cards_data[card2].get('image_path'):
                    img2 = f'<img src="{cards_data[card2]["image_path"]}" class="combo-card-img">'
            
            html_parts.append(f'''
            <div class="combo-item" data-tooltip="{text}">
                {img1 if img1 else '<span class="combo-placeholder">🃏</span>'}
                <span class="combo-plus">+</span>
                {img2 if img2 else '<span class="combo-placeholder">🃏</span>'}
                <span class="combo-text">{text}</span>
            </div>''')
        
        html_parts.append('        </div>')
    
    html_parts.extend([
        '    </div>',
        '</div>'
    ])
    
    return '\n'.join(html_parts)


def generate_archetype_section_html(
    archetype_name: str,
    cards: list[dict],
    combos: list[dict] = None,
    background_color: str = '#1a1a2e'
) -> str:
    """
    Generate complete HTML for an archetype section with cards and combo area.
    
    Args:
        archetype_name: Name of the archetype
        cards: List of card dictionaries in this archetype
        combos: Optional list of combos for this archetype
        background_color: Background color for the section
        
    Returns:
        Complete HTML string for archetype section
    """
    html_parts = [
        f'<div class="archetype-section" style="background: {background_color};">',
        f'    <h2 class="archetype-title">{archetype_name}</h2>',
        '    <div class="archetype-card-grid">'
    ]
    
    # Add cards sorted by value
    sorted_cards = sorted(cards, key=lambda c: c.get('value_score', 0), reverse=True)
    for card in sorted_cards:
        html_parts.append(generate_card_item_html(card))
    
    html_parts.append('    </div>')
    
    # Add combo section if combos exist
    if combos:
        html_parts.append(generate_combo_section_html(archetype_name, combos))
    
    html_parts.append('</div>')
    
    return '\n'.join(html_parts)
