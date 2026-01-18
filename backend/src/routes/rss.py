"""
API route for RSS feed.
"""
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from datetime import datetime
from src.database import get_db
from src.services.win_service import get_all_wins_sorted
from xml.etree.ElementTree import Element, SubElement, tostring

router = APIRouter(tags=["rss"])


def create_rss_feed(wins: list) -> str:
    """
    Create an RSS 2.0 feed from What Have Unions Done For Us.

    Args:
        wins: List of UnionWin instances sorted by date

    Returns:
        RSS XML string
    """
    # Create RSS root element
    rss = Element('rss')
    rss.set('version', '2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    rss.set('xmlns:dc', 'http://purl.org/dc/elements/1.1/')

    # Create channel element
    channel = SubElement(rss, 'channel')

    # Channel metadata
    title = SubElement(channel, 'title')
    title.text = 'What Have Unions Done For Us'

    link = SubElement(channel, 'link')
    link.text = 'https://unionwins.com'

    description = SubElement(channel, 'description')
    description.text = 'Recent victories and wins by labor unions across various sectors'

    language = SubElement(channel, 'language')
    language.text = 'en-us'

    # Add self-referencing atom:link
    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', 'https://unionwins.com/rss')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')

    # Add last build date (current time)
    last_build = SubElement(channel, 'lastBuildDate')
    last_build.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    # Add items for each win
    for win in wins:
        item = SubElement(channel, 'item')

        # Title with emoji if available
        item_title = SubElement(item, 'title')
        title_text = win.title
        if win.emoji:
            title_text = f"{win.emoji} {title_text}"
        item_title.text = title_text

        # Link to the original article
        item_link = SubElement(item, 'link')
        item_link.text = win.url

        # Description/summary
        item_desc = SubElement(item, 'description')
        desc_text = f"<![CDATA[{win.summary}]]>"
        # We'll handle CDATA manually in the final XML
        item_desc.text = win.summary

        # Publication date
        item_date = SubElement(item, 'pubDate')
        try:
            # Convert ISO date to RFC 822 format
            dt = datetime.fromisoformat(win.date)
            item_date.text = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        except (ValueError, AttributeError):
            # Fallback if date parsing fails
            item_date.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

        # GUID (unique identifier)
        guid = SubElement(item, 'guid')
        guid.set('isPermaLink', 'true')
        guid.text = win.url

        # Category for union name if available
        if win.union_name:
            category = SubElement(item, 'category')
            category.text = win.union_name

        # Enclosure for image
        if win.image:
            enclosure = SubElement(item, 'enclosure')
            enclosure.set('url', win.image)
            enclosure.set('type', 'image/jpeg')
            # Note: We don't have image size, setting a dummy value
            enclosure.set('length', '0')

    # Convert to string with proper XML declaration
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_string += tostring(rss, encoding='unicode', method='xml')

    return xml_string


@router.get("/rss", response_class=Response)
async def get_rss_feed(db: Session = Depends(get_db)) -> Response:
    """
    Get RSS feed of all What Have Unions Done For Us in reverse chronological order.

    Returns:
        RSS XML feed with all wins sorted by date (newest first)
    """
    wins = get_all_wins_sorted(db)
    rss_content = create_rss_feed(wins)

    return Response(
        content=rss_content,
        media_type="application/rss+xml",
        headers={
            "Content-Type": "application/rss+xml; charset=utf-8"
        }
    )
