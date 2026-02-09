"""
API route for proxying external images to avoid CORS issues.
"""
import base64
import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

router = APIRouter(prefix="/api/proxy", tags=["proxy"])


@router.get("/image")
async def proxy_image(url: str = Query(..., description="The URL of the image to proxy")):
    """
    Proxy an external image to avoid CORS issues.
    Returns the image with appropriate headers for browser display.
    """
    if not url:
        raise HTTPException(status_code=400, detail="URL parameter is required")
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; UnionWins/1.0)'
            })
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Failed to fetch image: {response.status_code}"
                )
            
            content_type = response.headers.get('content-type', 'image/jpeg')
            
            # Ensure it's an image
            if not content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail="URL does not point to an image")
            
            return Response(
                content=response.content,
                media_type=content_type,
                headers={
                    'Cache-Control': 'public, max-age=86400',
                    'Access-Control-Allow-Origin': '*'
                }
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request to image URL timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch image: {str(e)}")
