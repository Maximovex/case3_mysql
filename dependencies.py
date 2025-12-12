# Dependency functions for FastAPI
from crud import get_hotels,get_transfers,get_transports
from database import Hotels, Transfers, Transportations
from database import new_session

async def get_hotels_dependency() -> list[Hotels]:
    """Dependency to fetch all hotels"""
    return await get_hotels(new_session)

async def get_transfers_dependency() -> list[Transfers]:
    """Dependency to fetch all transfers"""
    return await get_transfers(new_session)

async def get_transports_dependency() -> list[Transportations]:
    """Dependency to fetch all transportations"""
    return await get_transports(new_session)