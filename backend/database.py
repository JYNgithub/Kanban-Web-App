from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import ssl
import os
from dotenv import load_dotenv

# Replace with PostgreSQL credentials
load_dotenv() 
DATABASE_URL = os.getenv('DATABASE_URL')

# SSL setup
ssl_context = ssl.create_default_context(cafile=None)
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context} 
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session