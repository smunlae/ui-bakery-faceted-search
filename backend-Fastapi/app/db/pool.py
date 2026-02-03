from typing import Optional

import asyncpg

from app.core.config import settings

_pool: Optional[asyncpg.pool.Pool] = None

async def get_pool() -> asyncpg.pool.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=1, max_size=10, command_timeout=30)
    return _pool

async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None