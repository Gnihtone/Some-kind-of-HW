from fastapi import FastAPI

from handlers import authentification, migrations, users_data

app = FastAPI()

app.include_router(authentification.router)
app.include_router(migrations.router)
app.include_router(users_data.router)
