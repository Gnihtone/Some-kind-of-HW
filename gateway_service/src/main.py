from fastapi import FastAPI

from handlers import users

app = FastAPI()

app.include_router(users.router)
