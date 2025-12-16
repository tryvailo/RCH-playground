"""
Proxy Routes for CORS bypass
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import Response

router = APIRouter(prefix="/api", tags=["Proxy"])


@router.post("/proxy-fetch")
async def proxy_fetch(url: str = Body(..., embed=True)):
    """Proxy fetch endpoint to avoid CORS issues when loading external files"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return Response(
                content=response.content,
                media_type=response.headers.get("content-type", "application/octet-stream"),
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "*",
                }
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy fetch failed: {str(e)}")
