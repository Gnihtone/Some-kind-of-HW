import logging
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_request(method: str, url: str, request) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        logger.info(request)
        return await client.request(method=method, url=url, json=request)
