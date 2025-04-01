from fastapi import APIRouter
from postgresql.migrations import V001__init_migration
from utils.postgresql import connect, execute_query, Connection

router = APIRouter()


migrations = {
    1: V001__init_migration.QUERY,
}


@router.post("/do-migration", status_code=200)
async def do_migrations(migration_version: int):
    with connect() as conn:
        execute_query(conn, 'COMMIT;')
        execute_query(conn, migrations[migration_version])
