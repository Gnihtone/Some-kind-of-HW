from fastapi import FastAPI

from handlers import migrations

app = FastAPI()

app.include_router(migrations.router)
