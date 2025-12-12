from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from settings import MY_DATABASE_URL, DB_ECHO

class DBHelper:
    """Database helper class to manage engine and session creation."""
    
    def __init__(self,url: str = MY_DATABASE_URL):
        self.engine = create_async_engine(url, echo=DB_ECHO)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def get_session(self):
        """Create and return a new asynchronous session."""
        async with self.async_session() as session:
            yield session

db_helper = DBHelper(url=MY_DATABASE_URL)