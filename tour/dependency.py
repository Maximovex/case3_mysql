from typing import Annotated

from fastapi import Depends, HTTPException, Path,status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import Tours
from db_helper import db_helper


async def get_tour_by_id_dependency(tour_id:int=Annotated[int,Path],session:AsyncSession=Depends(db_helper.session_dependency)):
    #tour = await get_tour_by_id(tour_id, session)
    tour = await session.execute(select(Tours).where(Tours.id == tour_id))
    tour = tour.scalar_one_or_none()

    if not tour:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tour not found")
        

    # hotels_list = await get_hotels(session)
    # transfers_list = await get_transfers(session)
    # transportations_list = await get_transports(session)

    return tour