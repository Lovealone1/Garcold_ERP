# app/db_conector.py

from dynaconf import Dynaconf
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = Dynaconf(
    settings_files=["config.yml"],
    load_dotenv=True
)

DATABASE_URL  = settings.database.url
DATABASE_ECHO = settings.database.echo

engine = create_async_engine(DATABASE_URL, echo=DATABASE_ECHO)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncSession:
    """
    Crea y entrega la sesión sin iniciar automáticamente una transacción.
    El servicio será quien abra/ cierre la transacción con `async with db.begin()`.
    """
    session = async_session()
    try:
        yield session
    finally:
        await session.close()
