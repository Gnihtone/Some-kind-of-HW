from datetime import datetime, timedelta
import logging
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sql.queries import (
    select_auth_data,
    insert_auth_data,
    insert_users_data,
    insert_tokens,
    select_auth_data_by_password,
)
from utils.postgresql import connect, execute_query, Connection
from utils.encoding import encode_password

import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class Error(BaseModel):
    code: str
    message: str


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


@router.post("/register/v1", status_code=201, responses={400: {"model": Error}})
async def register_v1(body: RegisterRequest):
    def validate_request():
        if len(body.password) < 8:
            return JSONResponse(
                    dict(
                        Error(
                            code="validation_error",
                            message="Too small password",
                        )
                    ),
                    400,
                )
    validate_request()

    with connect() as conn:
        with conn.begin():
            user_id = uuid.uuid4()

            data = execute_query(
                conn, select_auth_data.QUERY, username=body.username
            ).fetchall()
            if len(data) > 0:
                return JSONResponse(
                    dict(
                        Error(
                            code="already_exists",
                            message="User with same username already exists",
                        )
                    ),
                    400,
                )
            execute_query(
                conn,
                insert_auth_data.QUERY,
                user_id=user_id,
                username=body.username,
                encoded_password=encode_password(body.password),
            )
            execute_query(
                conn,
                insert_users_data.QUERY,
                user_id=user_id,
                name=body.name,
            )


@router.post(
    "/authorize/v1",
    response_model=AuthorizeResponse,
    responses={403: {}, 400: {"model": Error}},
)
async def authorize_v1(body: AuthorizeRequest):
    with connect() as conn:
        with conn.begin():
            encoded_password = encode_password(body.password)
            rows = execute_query(
                conn,
                select_auth_data_by_password.QUERY,
                username=body.username,
                encoded_password=encoded_password,
            ).fetchall()
            if len(rows) == 0:
                return Response(status_code=403)
            if len(rows) > 1:
                raise RuntimeError("Invariant failed, too many lines")

            row = rows[0]
            user_id = row[0]

            token = str(uuid.uuid4()) + "__" + str(uuid.uuid4())

            execute_query(
                conn,
                insert_tokens.QUERY,
                token=token,
                user_id=user_id,
                created_at="NOW()",
                active_until=datetime.now() + timedelta(hours=12),
            )

    return AuthorizeResponse(token=token)
