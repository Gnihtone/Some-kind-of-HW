from enum import Enum
import json
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, UUID4

from utils.send_request import proxy_request
from common.known_services import USERDATA_SERVICE_URL

router = APIRouter(prefix='/users')


class AuthentificationData(BaseModel):
    token: str
    user_id: UUID4


class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    surname: str


class AuthorizeRequest(BaseModel):
    username: str
    password: str


class AuthorizeResponse(BaseModel):
    auth_data: AuthentificationData


class Gender(str, Enum):
    undefined = 'undefined'
    male = 'male'
    female = 'female'


class UserDescriptor(BaseModel):
    user_id: UUID4
    version: int


class UserDataUpdatePayload(BaseModel):
    name: str
    surname: str
    status: str
    gender: Gender
    email: EmailStr | None
    phone_number: str | None


class UpdateRequest(BaseModel):
    descriptor: UserDescriptor
    payload: UserDataUpdatePayload
    auth_data: AuthentificationData


@router.post("/register/v1", status_code=201)
async def user_register_v1(body: RegisterRequest):
    return await proxy_request('POST', USERDATA_SERVICE_URL + '/register/v1', dict(body))


@router.post("/authorize/v1", status_code=200)
async def user_authorize_v1(body: AuthorizeRequest):
    return await proxy_request('POST', USERDATA_SERVICE_URL + '/authorize/v1', dict(body))


@router.post("/update/v1", status_code=200)
async def user_data_update(body: UpdateRequest):
    return await proxy_request('POST', USERDATA_SERVICE_URL + '/data/update/v1', dict(body), True)
