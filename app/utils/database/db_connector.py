from dynaconf import Dynaconf
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = Dynaconf(
    settings_files=["config.yml"],
    load_dotenv=True
)

DATABASE_URL = settings.database.url
DATABASE_ECHO = settings.database.echo

engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

__all__ = ["async_session", "get_db"]