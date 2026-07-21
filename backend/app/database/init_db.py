from app.auth.models import User
from app.database.base import Base
from app.database.session import engine


async def init_db():
    print("creating table",flush=True)
    async with engine.begin() as conn:
        print(Base.metadata.tables.keys(),flush=True)
        await conn.run_sync(Base.metadata.create_all)

    print("done",flush=True)