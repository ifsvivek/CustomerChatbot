import asyncpg
from config import POSTGRES_URL
import contextlib

_pool = None


async def init_db_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(POSTGRES_URL)
    return _pool


def get_db_pool():
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool


@contextlib.asynccontextmanager
async def get_db_connection():
    pool = await init_db_pool()
    async with pool.acquire() as connection:
        yield connection
