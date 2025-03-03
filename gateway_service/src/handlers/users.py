from fastapi import APIRouter, Response
from pydantic import BaseModel

from utils.send_request import send_request
from common.known_services import USERDATA_SERVICE_URL

router = APIRouter(prefix='/users')


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    surname: str


class AuthorizeRequest(BaseModel):
    username: str
    password: str


class AuthorizeResponse(BaseModel):
    token: str


@router.post("/register/v1", status_code=201)
async def user_register_v1(body: RegisterRequest):
    response = await send_request('POST', USERDATA_SERVICE_URL + '/register/v1', dict(body))
    if (response.status_code != 201):
        return Response(response.content, response.status_code)


@router.post("/authorize/v1", status_code=200)
async def user_authorize_v1(body: AuthorizeRequest):
    response = await send_request('POST', USERDATA_SERVICE_URL + '/authorize/v1', dict(body))
    if (response.status_code != 200):
        return Response(response.content, response.status_code)
    data = response.json()

    return AuthorizeResponse(token=data['token'])
