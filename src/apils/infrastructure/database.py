from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from apils.core.config import settings

if not settings.database_url:
    raise ValueError("DATABASE_URL must be set in .env")

DB_URL = settings.database_url

connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_async_engine(
    DB_URL,
    echo=False,
    connect_args=connect_args
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
