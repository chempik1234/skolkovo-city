from sqlalchemy import create_engine, StaticPool, NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session


def create_sqlalchemy_sessionmaker(url: str):
    try:
        session_class = AsyncSession
        engine = create_async_engine(
            url,
            poolclass=NullPool  # 500 IQ move to avoid "another event loop" error
        )
    except Exception as e:
        session_class = Session
        engine = create_engine(
            url, connect_args={"check_same_thread": False}
        )
    return sessionmaker(engine, expire_on_commit=False, class_=session_class)
