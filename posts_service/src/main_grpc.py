# posts_service/main.py
import logging
import uuid
from datetime import datetime
from typing import List

import asyncpg
import grpc
from google.protobuf.timestamp_pb2 import Timestamp
import asyncio
from grpc_reflection.v1alpha import reflection
from sqlalchemy import delete, func, select, update
from proto.posts_service_pb2 import (
    CreatePostRequest,
    GetPostRequest,
    UpdatePostRequest,
    DeletePostRequest,
    ListPostsRequest,
    PostResponse,
    ListPostsResponse,
    DeletePostResponse,
    DESCRIPTOR,
)
from proto.posts_service_pb2_grpc import PostServiceServicer, add_PostServiceServicer_to_server
from utils.postgresql import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    async def create_post(self, post_id: str, creator_user_id: str, title: str, content: str, 
                         is_private: bool, tags: List[str]) -> None:
        with connect() as conn:
            with conn.begin():
                query = text("""
                    INSERT INTO posts_data 
                    (post_id, creator_user_id, title, content, is_private, tags)
                    VALUES (:post_id, :creator_user_id, :title, :content, :is_private, :tags)
                    RETURNING *
                """)
                return conn.execute(
                    query,
                    {
                        "post_id": str(post_id),
                        "creator_user_id": str(creator_user_id),
                        "title": title,
                        "content": content,
                        "is_private": is_private,
                        "tags": tags
                    }
                ).fetchone()

    async def get_post(self, post_id: str) -> asyncpg.Record:
        with connect() as conn:
            query = select(text("*")).select_from(text("posts_data")).where(text("post_id = :post_id"))
            result = conn.execute(query, {"post_id": str(post_id)})
            return result.fetchone()

    async def update_post(self, post_id: str, title: str, content: str, 
                          is_private: bool, tags: List[str]) -> None:
        with connect() as conn:
            with conn.begin():
                stmt = """
                    UPDATE posts_data
                    SET
                        title = :title,
                        content = :content,
                        is_private = :is_private,
                        tags = :tags
                    WHERE post_id = :post_id
                    RETURNING *
                """
                return conn.execute(text(stmt), {"title": title, "content": content, "is_private": is_private, "tags": tags, "post_id": str(post_id)}).fetchone()

    async def delete_post(self, post_id: str) -> bool:
        with connect() as conn:
            with conn.begin():
                stmt = """
                    DELETE FROM posts_data WHERE post_id = :post_id
                """
                result = conn.execute(text(stmt), {"post_id": str(post_id)})
                return result.rowcount > 0

    async def list_posts(self, page: int, per_page: int) -> List[asyncpg.Record]:
        with connect() as conn:
            offset = (page - 1) * per_page
            query = """
                SELECT * FROM posts_data
                WHERE is_private = FALSE
                ORDER BY created_at DESC
                LIMIT :per_page
                OFFSET :offset
            """
            result = conn.execute(text(query), {"per_page": per_page, "offset": offset})
            return result.fetchall()

    async def count_posts(self) -> int:
        with connect() as conn:
            query = select(func.count()).select_from(text("posts_data"))
            result = conn.execute(query)
            return result.scalar()


class PostService(PostServiceServicer):
    def __init__(self, db: Database):
        self.db = db

    async def CreatePost(self, request: CreatePostRequest, context) -> PostResponse:
        post_id = str(uuid.uuid4())
        return await self._record_to_response(await self.db.create_post(
            post_id=post_id,
            creator_user_id=request.creator_user_id,
            title=request.title,
            content=request.content,
            is_private=request.is_private,
            tags=list(request.tags)
        ))

    async def GetPost(self, request: GetPostRequest, context) -> PostResponse:
        return await self._get_post_response(request.post_id, context)

    async def UpdatePost(self, request: UpdatePostRequest, context) -> PostResponse:
        return await self._record_to_response(await self.db.update_post(
            post_id=request.post_id,
            title=request.title,
            content=request.content,
            is_private=request.is_private,
            tags=list(request.tags)
        ))

    async def DeletePost(self, request, context: grpc.ServicerContext):
        post = await self.db.get_post(request.post_id)
        if not post:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")

        if str(post[1]) != request.user_id:
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission denied")

        success = await self.db.delete_post(request.post_id)
        return DeletePostResponse(success=success)

    async def ListPosts(self, request: ListPostsRequest, context) -> ListPostsResponse:
        posts = await self.db.list_posts(request.page, request.per_page)
        total = await self.db.count_posts()
        return ListPostsResponse(
            posts=[await self._record_to_response(post) for post in posts],
            total=total
        )

    async def _get_post_response(self, post_id: str, context: grpc.ServicerContext) -> PostResponse:
        post = await self.db.get_post(post_id)
        logger.info(post)
        if not post:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Post not found")
        return await self._record_to_response(post)

    async def _record_to_response(self, post: asyncpg.Record) -> PostResponse:
        created_at = Timestamp()
        created_at.FromDatetime(post[5])
        updated_at = Timestamp()
        updated_at.FromDatetime(post[6])

        post_id = post[0]
        title=post[2]
        content=post[3]
        creator_user_id=post[1]
        is_private=post[7]
        tags=post[8]
    
        return PostResponse(
            post_id=str(post_id),
            title=title,
            content=content,
            creator_user_id=str(creator_user_id),
            created_at=created_at,
            updated_at=updated_at,
            is_private=is_private,
            tags=tags
        )


async def serve():
    # TODO: Вынести в env
    
    db = Database()

    print("gRPC server started")
    server = grpc.aio.server()
    add_PostServiceServicer_to_server(PostService(db), server)
    
    SERVICE_NAMES = (
        DESCRIPTOR.services_by_name["PostService"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    server.add_insecure_port('0.0.0.0:50051')
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
