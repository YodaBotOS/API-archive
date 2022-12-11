import asyncio
import typing

import asyncpg

import config


async def add_tables(db):
    with open("schema.sql", "r") as f:
        query = f.read()

    async with db.acquire() as conn:
        await conn.execute(query)


def init_db(sync=True) -> asyncpg.Pool | typing.Coroutine[None, None, asyncpg.Pool]:
    if sync:
        loop = asyncio.get_event_loop()
        db = loop.run_until_complete(asyncpg.create_pool(config.DATABASE_URL))
        loop.run_until_complete(add_tables(db))

        return db
    else:
        async def x():
            db = await asyncpg.create_pool(config.DATABASE_URL)
            await add_tables(db)

            return db

        return x()
