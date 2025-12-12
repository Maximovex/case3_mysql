from schemas import SHotelsAdd, SHotels
from database import Hotels
from sqlalchemy import select
from db_helper import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def add_hotel(
    hotel: SHotelsAdd, session: AsyncSession = Depends(db_helper.session_dependency)
) -> Hotels:
    """Add a new hotel to the database"""

    new_hotel = Hotels(**hotel.model_dump())
    session.add(new_hotel)
    await session.flush()

    return new_hotel


async def get_hotels(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Hotels]:
    """Fetch all hotels"""
    hotels = await session.execute(select(Hotels))
    return hotels.scalars().all()
