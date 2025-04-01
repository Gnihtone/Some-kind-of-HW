import pytest
from datetime import datetime
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from google.protobuf import timestamp_pb2
import grpc

from src.main import app
from src.proto.posts_service_pb2 import (
    PostResponse as GrpcPostResponse,
    ListPostsResponse as GrpcListPostsResponse,
    DeletePostResponse as GrpcDeletePostResponse
)

@pytest.fixture
async def mock_grpc_channel():
    with patch('grpc.aio.insecure_channel') as mock_channel:
        mock_channel.return_value = AsyncMock()
        yield mock_channel

@pytest.fixture
async def mock_post_service(mock_grpc_channel):
    with patch('post_service_pb2_grpc.PostServiceStub') as mock_stub:
        mock_service = AsyncMock()
        mock_stub.return_value = mock_service
        yield mock_service

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

def create_grpc_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(dt)
    return ts

@pytest.mark.asyncio
async def test_create_post_success(client, mock_post_service):
    test_time = datetime(2023, 1, 1, 12, 0)
    mock_post_service.CreatePost.return_value = GrpcPostResponse(
        post_id="post123",
        title="Test Post",
        content="Test Content",
        creator_user_id="user123",
        created_at=create_grpc_timestamp(test_time),
        updated_at=create_grpc_timestamp(test_time),
        is_private=False,
        tags=["test"]
    )

    response = await client.post(
        "/posts",
        json={
            "title": "Test Post",
            "content": "Test Content",
            "creator_user_id": "user123",
            "is_private": False,
            "tags": ["test"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == "post123"
    assert data["title"] == "Test Post"
    assert data["content"] == "Test Content"
    assert data["created_at"] == "2023-01-01T12:00:00"
    assert data["tags"] == ["test"]

@pytest.mark.asyncio
async def test_get_post_success(client, mock_post_service):
    test_time = datetime(2023, 1, 1, 12, 0)
    mock_post_service.GetPost.return_value = GrpcPostResponse(
        post_id="post123",
        title="Test Post",
        content="Test Content",
        creator_user_id="user123",
        created_at=create_grpc_timestamp(test_time),
        updated_at=create_grpc_timestamp(test_time),
        is_private=False,
        tags=[]
    )

    response = await client.get("/posts/post123")
    assert response.status_code == 200
    data = response.json()
    assert data["post_id"] == "post123"

@pytest.mark.asyncio
async def test_get_post_not_found(client, mock_post_service):
    mock_post_service.GetPost.side_effect = grpc.RpcError(
        code=grpc.StatusCode.NOT_FOUND
    )
    
    response = await client.get("/posts/invalid_id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"

@pytest.mark.asyncio
async def test_update_post_success(client, mock_post_service):
    test_time = datetime(2023, 1, 1, 12, 0)
    mock_post_service.UpdatePost.return_value = GrpcPostResponse(
        post_id="post123",
        title="Updated Title",
        content="Updated Content",
        creator_user_id="user123",
        created_at=create_grpc_timestamp(test_time),
        updated_at=create_grpc_timestamp(test_time),
        is_private=True,
        tags=["updated"]
    )

    response = await client.patch(
        "/posts/post123",
        json={
            "title": "Updated Title",
            "content": "Updated Content",
            "is_private": True,
            "tags": ["updated"]
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_private"] is True

@pytest.mark.asyncio
async def test_delete_post_success(client, mock_post_service):
    mock_post_service.DeletePost.return_value = GrpcDeletePostResponse(success=True)
    
    response = await client.delete(
        "/posts/post123",
        headers={"X-User-Id": "user123"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.asyncio
async def test_delete_post_permission_denied(client, mock_post_service):
    mock_post_service.DeletePost.side_effect = grpc.RpcError(
        code=grpc.StatusCode.PERMISSION_DENIED
    )
    
    response = await client.delete(
        "/posts/post123",
        headers={"X-User-Id": "wrong_user"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"

@pytest.mark.asyncio
async def test_list_posts(client, mock_post_service):
    test_time = datetime(2023, 1, 1, 12, 0)
    mock_post_service.ListPosts.return_value = GrpcListPostsResponse(
        posts=[
            GrpcPostResponse(
                post_id="post1",
                title="Post 1",
                content="Content 1",
                creator_user_id="user1",
                created_at=create_grpc_timestamp(test_time),
                updated_at=create_grpc_timestamp(test_time),
                is_private=False,
                tags=[]
            )
        ],
        total=1
    )

    response = await client.post(
        "/posts/list",
        json={"page": 1, "per_page": 10}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) == 1
    assert data["total"] == 1
    assert data["posts"][0]["title"] == "Post 1"

@pytest.mark.asyncio
async def test_create_post_validation(client):
    response = await client.post(
        "/posts",
        json={
            "title": "A" * 256,
            "content": "Content",
            "creator_user_id": "invalid-uuid"
        }
    )
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(e["loc"] == ["body", "title"] for e in errors)
    assert any(e["loc"] == ["body", "creator_user_id"] for e in errors)
