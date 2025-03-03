from fastapi import FastAPI

from handlers import authentification, migrations

app = FastAPI()

app.include_router(authentification.router)
app.include_router(migrations.router)
