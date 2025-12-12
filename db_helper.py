from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from settings import MY_DATABASE_URL, DB_ECHO
from asyncio import current_task


class DBHelper:
    """Database helper class to manage engine and session creation."""

    def __init__(self, url: str = MY_DATABASE_URL):
        self.engine = create_async_engine(url, echo=DB_ECHO)
        self.async_session = async_sessionmaker(
            self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    def get_scoped_session(self):
        """Create and return a new asynchronous session."""
        session = async_scoped_session(self.async_session, scopefunc=current_task)
        return session
 
    async def session_dependency(self) -> AsyncSession:
        """Dependency to provide a session for FastAPI routes."""
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.remove()


db_helper = DBHelper(url=MY_DATABASE_URL)
