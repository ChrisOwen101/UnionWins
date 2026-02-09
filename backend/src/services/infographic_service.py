"""
Service for generating infographic images from wins data.
Uses Pillow to create PNG images directly.
"""
import io
from typing import List
from datetime import datetime, timedelta
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
from src.schemas import UnionWin


def get_period_colors(period: str) -> tuple:
    """Get color for period."""
    colors = {
        'week': (249, 115, 22),      # orange
        'month': (59, 130, 246),     # blue
        'year': (34, 197, 94)        # green
    }
    return colors.get(period, colors['week'])


def get_period_label(period: str) -> tuple[str, str]:
    """Get period label and dates."""
    end = datetime.now()
    
    if period == 'week':
        start = end - timedelta(days=7)
        label = 'This Week'
    elif period == 'month':
        start = end - timedelta(days=30)
        label = 'This Month'
    else:  # year
        start = end - timedelta(days=365)
        label = 'This Year'
    
    dates = f"{start.strftime('%d %b %Y')} - {end.strftime('%d %b %Y')}"
    return label, dates


async def generate_infographic_image(wins: List[UnionWin], period: str) -> bytes:
    """
    Generate a PNG infographic image from wins data.
    
    Args:
        wins: List of union wins to include
        period: Time period ('week', 'month', or 'year')
        
    Returns:
        PNG image as bytes
    """
    # Image dimensions
    width, height = 600, 800
    
    # Create image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Load fonts (use default if custom not available)
    try:
        title_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 24)
        header_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 18)
        big_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 64)
        medium_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
        small_font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 12)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        header_font = ImageFont.load_default()
        big_font = ImageFont.load_default()
        medium_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Get period info
    label, dates = get_period_label(period)
    color1 = get_period_colors(period)
    
    # Draw header with gradient background (simplified - solid color)
    draw.rectangle([(0, 0), (width, 180)], fill=color1)
    
    # Draw emoji and title
    draw.text((20, 20), '📣', font=title_font, fill=(255, 255, 255))
    draw.text((70, 25), f'Union Wins {label}', font=title_font, fill=(255, 255, 255))
    draw.text((70, 55), dates, font=small_font, fill=(255, 255, 255, 204))
    
    # Draw big number
    total_wins = len(wins)
    wins_text = str(total_wins)
    draw.text((width//2 - 30, 90), wins_text, font=big_font, fill=(255, 255, 255), anchor='mm')
    draw.text((width//2, 140), f"{'Victory' if total_wins == 1 else 'Victories'} for Workers", 
              font=medium_font, fill=(255, 255, 255), anchor='mm')
    
    # Stats section
    y_offset = 200
    
    # Calculate stats
    union_counts = Counter(win.union_name or 'Unknown' for win in wins)
    type_counts = Counter()
    for win in wins:
        types = (win.win_types or 'Other').split(',')
        for t in types:
            type_counts[t.strip()] += 1
    
    # Top unions
    top_unions = union_counts.most_common(3)
    
    # Draw "Most Active Unions" section
    draw.text((20, y_offset), '🏆 Most Active Unions', font=header_font, fill=(31, 41, 55))
    y_offset += 35
    
    for i, (union, count) in enumerate(top_unions):
        bg_color = color1 if i == 0 else (243, 244, 246)
        text_color = (255, 255, 255) if i == 0 else (55, 65, 81)
        
        # Draw rounded rectangle (simplified)
        tag_y = y_offset + i * 35
        draw.rounded_rectangle([(20, tag_y), (280, tag_y + 28)], radius=14, fill=bg_color)
        medal = '🥇 ' if i == 0 else ''
        draw.text((30, tag_y + 5), f'{medal}{union} ({count})', font=small_font, fill=text_color)
    
    y_offset += 120
    
    # Recent pay rises
    pay_rises = [w for w in wins if 'pay rise' in (w.win_types or '').lower()]
    pay_rises.sort(key=lambda x: x.date, reverse=True)
    pay_rises = pay_rises[:3]
    
    if pay_rises:
        draw.text((20, y_offset), '💰 Recent Pay Rises', font=header_font, fill=(31, 41, 55))
        y_offset += 35
        
        for rise in pay_rises:
            # Draw rounded rectangle background
            draw.rounded_rectangle([(20, y_offset), (width - 20, y_offset + 50)], 
                                  radius=8, fill=(254, 243, 199))
            
            # Title (truncate if needed)
            title = rise.title[:50] + '...' if len(rise.title) > 50 else rise.title
            draw.text((30, y_offset + 8), title, font=small_font, fill=(120, 53, 15))
            draw.text((30, y_offset + 28), rise.union_name or 'Union', font=small_font, fill=(146, 64, 14))
            y_offset += 60
    
    # Footer
    draw.text((width//2, height - 30), 'Find out more at whathaveunionsdoneforus.uk', 
              font=small_font, fill=(107, 114, 128), anchor='mm')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()
