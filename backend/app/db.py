from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

engine = create_engine(get_settings().postgres_dsn, pool_pre_ping=True, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(engine, expire_on_commit=False)
