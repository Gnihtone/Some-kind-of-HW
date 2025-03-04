import logging
import httpx

from fastapi import Response
from fastapi.encoders import jsonable_encoder

from common.known_services import USERDATA_SERVICE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_request(method: str, url: str, request: dict) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        logger.info(request)
        return await client.request(method=method, url=url, json=jsonable_encoder(request))


async def proxy_request(method: str, url: str, request: dict, need_auth: bool = False) -> Response:
    if need_auth:
        auth_data = request.pop('auth_data')
        auth_response = await send_request('POST', USERDATA_SERVICE_URL+'/check-token/v1', {'token': auth_data.token, 'user_id': auth_data.user_id})
        if auth_response.status_code != 200:
            return Response(status_code=403)
    response = await send_request(method, url, request)
    return Response(response.content, response.status_code)
