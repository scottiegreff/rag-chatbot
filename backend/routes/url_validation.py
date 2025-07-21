from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import asyncio
from typing import Optional
import logging

router = APIRouter(prefix="/api", tags=["url-validation"])

logger = logging.getLogger(__name__)

class URLValidationRequest(BaseModel):
    url: str
    timeout: Optional[int] = 5000

class URLValidationResponse(BaseModel):
    valid: bool
    status: int
    error: Optional[str] = None
    final_url: Optional[str] = None
    content_type: Optional[str] = None

@router.post("/validate-url", response_model=URLValidationResponse)
async def validate_url(request: URLValidationRequest):
    """
    Validate if a URL is accessible (not 404)
    """
    try:
        # Basic URL validation
        if not request.url.startswith(('http://', 'https://')):
            return URLValidationResponse(
                valid=False,
                status=0,
                error="Invalid URL format - must start with http:// or https://"
            )

        # Set up headers to mimic a real browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        timeout = httpx.Timeout(request.timeout / 1000)  # Convert ms to seconds
        
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.head(request.url, headers=headers)
            
            # Check if the response is successful
            valid = 200 <= response.status_code < 400
            
            return URLValidationResponse(
                valid=valid,
                status=response.status_code,
                final_url=str(response.url),
                content_type=response.headers.get('content-type'),
                error=None if valid else f"HTTP {response.status_code}"
            )

    except httpx.TimeoutException:
        return URLValidationResponse(
            valid=False,
            status=0,
            error="Request timeout"
        )
    except httpx.ConnectError:
        return URLValidationResponse(
            valid=False,
            status=0,
            error="Connection error - unable to reach the server"
        )
    except httpx.HTTPStatusError as e:
        return URLValidationResponse(
            valid=False,
            status=e.response.status_code,
            error=f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
        )
    except Exception as e:
        logger.error(f"Error validating URL {request.url}: {str(e)}")
        return URLValidationResponse(
            valid=False,
            status=0,
            error=f"Validation error: {str(e)}"
        )

@router.post("/validate-urls-batch")
async def validate_urls_batch(urls: list[str]):
    """
    Validate multiple URLs in parallel
    """
    tasks = []
    for url in urls:
        task = validate_url(URLValidationRequest(url=url))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "url": urls[i],
                "valid": False,
                "status": 0,
                "error": str(result)
            })
        else:
            processed_results.append({
                "url": urls[i],
                **result.dict()
            })
    
    return processed_results 