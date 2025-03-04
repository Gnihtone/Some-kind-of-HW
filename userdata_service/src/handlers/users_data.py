from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import re
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, UUID4, EmailStr
from sql.queries import (
    update_auth_data,
    update_user_data,
)

from common.models import Error
from utils.postgresql import connect, execute_query, Connection
from utils.encoding import encode_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


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


@router.post("/data/update/v1", status_code=200, responses={400: {"model": Error}})
async def update_v1(body: UpdateRequest):
    def validate():
        if not re.match(r'/^\+?[1-9][0-9]{7,14}$/', body.payload.phone_number):
            return JSONResponse(
                    dict(
                        Error(
                            code="validation_error",
                            message="Too small password",
                        )
                    ),
                    400,
                )
    validate()

    with connect() as conn:
        with conn.begin():
            user_id = body.descriptor.user_id
            payload = body.payload

            execute_query(
                conn,
                update_user_data.QUERY,
                user_id=user_id,
                name=payload.name,
                surname=payload.surname,
                gender=payload.gender,
                status=payload.status,
            )
            execute_query(
                conn,
                update_auth_data.QUERY,
                user_id=user_id,
                phone_number=payload.phone_number,
                email=payload.email
            )
