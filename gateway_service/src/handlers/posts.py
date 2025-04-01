# gateway/main.py
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, FastAPI, HTTPException, Header, Response
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from pydantic import UUID4, BaseModel
from common.known_services import USERDATA_SERVICE_URL
from proto.posts_service_pb2 import (
    CreatePostRequest as GrpcCreatePostRequest,
    GetPostRequest as GrpcGetPostRequest,
    UpdatePostRequest as GrpcUpdatePostRequest,
    DeletePostRequest as GrpcDeletePostRequest,
    ListPostsRequest as GrpcListPostsRequest,
)
from utils.send_request import send_request
from proto.posts_service_pb2_grpc import PostServiceStub


router = APIRouter(prefix='/posts')


class AuthentificationData(BaseModel):
    token: str
    user_id: UUID4


class GetPostRequest(BaseModel):
    auth_data: AuthentificationData

class DeletePostRequest(BaseModel):
    auth_data: AuthentificationData

class CreatePostRequest(BaseModel):
    auth_data: AuthentificationData
    title: str
    content: str
    creator_user_id: str
    is_private: bool = False
    tags: List[str] = []

class UpdatePostRequest(BaseModel):
    auth_data: AuthentificationData
    title: Optional[str] = None
    content: Optional[str] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

class ListPostsRequest(BaseModel):
    page: int = 1
    per_page: int = 10

class PostResponse(BaseModel):
    post_id: str
    title: str
    content: str
    creator_user_id: str
    created_at: datetime
    updated_at: datetime
    is_private: bool
    tags: List[str]

class ListPostsResponse(BaseModel):
    posts: List[PostResponse]
    total: int

def _convert_timestamp(ts: Timestamp) -> datetime:
    return ts.ToDatetime().replace(tzinfo=None)

@router.post("/", response_model=PostResponse)
async def create_post(request: CreatePostRequest):
    auth_data = request.auth_data
    auth_response = await send_request('POST', USERDATA_SERVICE_URL+'/check-token/v1', {'token': auth_data.token, 'user_id': auth_data.user_id})
    if request.creator_user_id != str(auth_data.user_id) or auth_response.status_code != 200:
        return Response(status_code=403)

    async with grpc.aio.insecure_channel("posts-grpc-service:50051") as channel:
        stub = PostServiceStub(channel)
        response = await stub.CreatePost(
            GrpcCreatePostRequest(
                title=request.title,
                content=request.content,
                creator_user_id=request.creator_user_id,
                is_private=request.is_private,
                tags=request.tags,
            )
        )
        return PostResponse(
            post_id=response.post_id,
            title=response.title,
            content=response.content,
            creator_user_id=response.creator_user_id,
            created_at=_convert_timestamp(response.created_at),
            updated_at=_convert_timestamp(response.updated_at),
            is_private=response.is_private,
            tags=list(response.tags),
        )

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: str, x_user_id: str = Header(..., alias="X-User-Id"), x_auth_token: str = Header(..., alias="X-Auth-Token")):
    auth_response = await send_request('POST', USERDATA_SERVICE_URL+'/check-token/v1', {'token': x_auth_token, 'user_id': x_user_id})
    if auth_response.status_code != 200:
        return Response(status_code=403)

    async with grpc.aio.insecure_channel("posts-grpc-service:50051") as channel:
        stub = PostServiceStub(channel)
        try:
            response = await stub.GetPost(GrpcGetPostRequest(post_id=post_id))
            if response.is_private and x_user_id != response.creator_user_id:
                return Response(status_code=403)
            return PostResponse(
                post_id=response.post_id,
                title=response.title,
                content=response.content,
                creator_user_id=response.creator_user_id,
                created_at=_convert_timestamp(response.created_at),
                updated_at=_convert_timestamp(response.updated_at),
                is_private=response.is_private,
                tags=list(response.tags),
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise HTTPException(status_code=404, detail="Post not found")
            raise

@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, request: UpdatePostRequest):
    auth_data = request.auth_data
    auth_response = await send_request('POST', USERDATA_SERVICE_URL+'/check-token/v1', {'token': auth_data.token, 'user_id': auth_data.user_id})
    if auth_response.status_code != 200:
        return Response(status_code=403)

    async with grpc.aio.insecure_channel("posts-grpc-service:50051") as channel:
        stub = PostServiceStub(channel)
        try:
            response = await stub.UpdatePost(
                GrpcUpdatePostRequest(
                    post_id=post_id,
                    title=request.title,
                    content=request.content,
                    is_private=request.is_private,
                    tags=request.tags or [],
                )
            )
            return PostResponse(
                post_id=response.post_id,
                title=response.title,
                content=response.content,
                creator_user_id=response.creator_user_id,
                created_at=_convert_timestamp(response.created_at),
                updated_at=_convert_timestamp(response.updated_at),
                is_private=response.is_private,
                tags=list(response.tags),
            )
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise HTTPException(status_code=404, detail="Post not found")
            raise

@router.delete("/{post_id}")
async def delete_post(
    post_id: str, 
    request: DeletePostRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
):
    auth_data = request.auth_data
    auth_response = await send_request('POST', USERDATA_SERVICE_URL+'/check-token/v1', {'token': auth_data.token, 'user_id': auth_data.user_id})
    if x_user_id != str(auth_data.user_id) or auth_response.status_code != 200:
        return Response(status_code=403)

    async with grpc.aio.insecure_channel("posts-grpc-service:50051") as channel:
        stub = PostServiceStub(channel)
        try:
            response = await stub.DeletePost(
                GrpcDeletePostRequest(post_id=post_id, user_id=x_user_id))
            return {"success": response.success}
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                raise HTTPException(status_code=404, detail="Post not found")
            elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
                raise HTTPException(status_code=403, detail="Permission denied")
            raise

@router.post("/list", response_model=ListPostsResponse)
async def list_posts(request: ListPostsRequest = Body(...)):
    async with grpc.aio.insecure_channel("posts-grpc-service:50051") as channel:
        stub = PostServiceStub(channel)
        response = await stub.ListPosts(
            GrpcListPostsRequest(page=request.page, per_page=request.per_page)
        )
        return ListPostsResponse(
            posts=[
                PostResponse(
                    post_id=post.post_id,
                    title=post.title,
                    content=post.content,
                    creator_user_id=post.creator_user_id,
                    created_at=_convert_timestamp(post.created_at),
                    updated_at=_convert_timestamp(post.updated_at),
                    is_private=post.is_private,
                    tags=list(post.tags),
                )
                for post in response.posts
            ],
            total=response.total,
        )
