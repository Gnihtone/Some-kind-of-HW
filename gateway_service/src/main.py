from fastapi import FastAPI

from handlers import users, posts

app = FastAPI()

app.include_router(users.router)
app.include_router(posts.router)
