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
