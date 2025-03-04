from pathlib import Path
from sqlalchemy import Connection, CursorResult, create_engine, text

# TODO: Вынести в env
engine = create_engine('postgresql+psycopg2://postgres_user:postgres_password@postgres-userdata:5432/userdata')

def connect() -> Connection:
    return engine.connect()

def disconnect(connection: Connection):
    connection.close()

def execute_query(conn: Connection, sql: str, **kwargs) -> CursorResult:
    return conn.execute(text(sql), kwargs)

def with_database_connect(handler):
    connection = connect()
    def wrapper(*args, **kwargs):
        return handler(*args, **kwargs, connection=connection)
    disconnect(connection)

    return wrapper
