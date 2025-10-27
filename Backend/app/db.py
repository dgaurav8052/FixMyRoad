import os
import asyncpg
from .config import settings

async def get_db():
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        yield conn
    finally:
        await conn.close()
