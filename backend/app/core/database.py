from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

egine = create_async_engine(
    settings.DATABASE_URL,
    echo = True,
    pool_size = 5,
    max_overflow = 10,
)