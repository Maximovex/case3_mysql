from sqlalchemy import select
from database import (
    Base,
    Tours,
    Customers,
    Orders,
    Managers,
    Transfers,
    Hotels,
    Transportations,
)
from crud import get_transfers_by_id
from .dependency import get_tour_by_id_dependency
from schemas import (
    SToursAdd,
    STours,
    SToursUpdate,
    STransportAdd,
    STransport,
    STransferAdd,
    STransfer,
    SHotelsAdd,
    SHotels,
    SCustomersAdd,
    SCustomers,
    SOrdersAdd,
)
from db_helper import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_tours_detailed(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[STours]:
    """Fetch all tours with related hotel, transfer, and transportation details"""

    tours = await session.execute(select(Tours))
    tours = tours.scalars().all()

    result = []

    for tour in tours:
        # Convert Tours ORM model to STours Pydantic schema using model_validate
        tour_schema = STours.model_validate(tour)

        # Fetch and add hotel details if hotels_id exists
        if tour.hotels_id:
            hotel = await session.execute(
                select(Hotels).where(Hotels.id == tour.hotels_id)
            )
            hotel = hotel.scalar_one_or_none()
            if hotel:
                tour_schema.hotel = SHotels.model_validate(hotel)

        # Fetch and add transfer details if transfer_id exists
        if tour.transfer_id:
            transfer = await get_transfers_by_id(tour.transfer_id, session)
            tour_schema.transfer = STransfer.model_validate(transfer)

        # Fetch and add transport details if transport_id exists
        if tour.transport_id:
            transport = await session.execute(
                select(Transportations).where(Transportations.id == tour.transport_id)
            )
            transport = transport.scalar_one_or_none()
            if transport:
                tour_schema.transport = STransport.model_validate(transport)
        # Calculate total cost
        total_cost = 0
        if tour_schema.hotel and tour_schema.hotel.price:
            total_cost += tour_schema.hotel.price
        if tour_schema.transfer and tour_schema.transfer.price:
            total_cost += tour_schema.transfer.price
        if tour_schema.transport and tour_schema.transport.price:
            total_cost += tour_schema.transport.price
        tour_schema.total_cost = total_cost
        result.append(tour_schema)

    return result


async def update_tour(
    tour: SToursUpdate,
    tour_obj=Depends(get_tour_by_id_dependency),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Tours | None:
    """Update an existing tour"""
    
    if not tour_obj:
        return None

    
    for key, value in tour.model_dump(exclude_unset=True).items():
        setattr(tour_obj, key, value)
  

    
    await session.flush()
    await session.commit()
    return tour_obj


async def delete_tour(
    tour_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
) -> bool:
    """Delete a tour"""
    tour = await session.execute(select(Tours).where(Tours.id == tour_id))
    tour = tour.scalar_one_or_none()

    if not tour:
        return False

    await session.delete(tour)
    await session.commit()
    return True


async def get_tour_by_id(
    tour_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
) -> STours | None:
    """Fetch a single tour with all related data"""
    tour = await session.execute(select(Tours).where(Tours.id == tour_id))
    tour = tour.scalar_one_or_none()

    if not tour:
        return None
    tour_schema = STours.model_validate(tour)

    # Fetch related hotel
    if tour.hotels_id:
        hotel = await session.execute(select(Hotels).where(Hotels.id == tour.hotels_id))
        hotel = hotel.scalar_one_or_none()
        if hotel:
            tour_schema.hotel = SHotels.model_validate(hotel)

    # Fetch related transport
    if tour.transport_id:
        transport = await session.execute(
            select(Transportations).where(Transportations.id == tour.transport_id)
        )
        transport = transport.scalar_one_or_none()
        if transport:
            tour_schema.transport = STransport.model_validate(transport)

    # Fetch related transfer
    if tour.transfer_id:
        transfer = await session.execute(
            select(Transfers).where(Transfers.id == tour.transfer_id)
        )
        transfer = transfer.scalar_one_or_none()
        if transfer:
            tour_schema.transfer = STransfer.model_validate(transfer)

    return tour_schema


async def add_tour(
    tour: SToursAdd, session: AsyncSession = Depends(db_helper.session_dependency)
) -> Tours:
    """Add a new tour to the database"""
    new_tour = Tours(**tour.model_dump())
    session.add(new_tour)
    await session.flush()
    return new_tour


