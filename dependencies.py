from fastapi import Depends
from crud import get_transfers, get_transports
from hotel.crud import get_hotels
from database import Hotels, Transfers, Transportations

from sqlalchemy.ext.asyncio import AsyncSession
from db_helper import db_helper


async def get_hotels_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Hotels]:
    """Dependency to fetch all hotels"""
    return await get_hotels(session)

async def get_transfers_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Transfers]:
    """Dependency to fetch all transfers"""
    return await get_transfers(session)

async def get_transports_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Transportations]:
    """Dependency to fetch all transportations"""
    return await get_transports(session)