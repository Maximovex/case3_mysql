from typing import Annotated
from fastapi import Depends, HTTPException, Path,status
from crud import get_transfers, get_transports
from tour.crud import get_tours_detailed
from hotel.crud import get_hotels
from customer.crud import get_customers
from manager.crud import get_manager_by_id, get_managers
from database import Hotels, Transfers, Transportations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_helper import db_helper
from database import Tours
from schemas import SOrders, STours,SCustomers,SHotels,STransfer,STransport,SManagers


async def get_hotels_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Hotels]:
    """Dependency to fetch all hotels"""
    return await get_hotels(session)

async def get_hotel_by_id_dependency(
    hotel_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Hotels | None:
    """Dependency to fetch a hotel by its ID"""
    hotel = await session.execute(
        select(Hotels).where(Hotels.id == hotel_id)
    )
    return hotel.scalar_one_or_none()

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

async def get_tours_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[STours]:
    """Dependency to fetch all tours"""
    return await get_tours_detailed(session)

async def get_customers_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[SCustomers]:
    """Dependency to fetch all customers"""
    return await get_customers(session)
async def get_managers_dependency(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[SManagers]:
    """Dependency to fetch all managers"""
    return await get_managers(session)
async def get_manager_by_id_dependency(
    manager_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> SManagers | None:
    """Dependency to fetch a manager by ID"""
    return await get_manager_by_id(manager_id, session)

