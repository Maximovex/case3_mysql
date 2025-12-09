from sqlalchemy import select
from database import Base, Tours, Customers, Orders, Managers, Transfers, Hotels, Transportations,new_session,AsyncSession
from schemas import SToursAdd, STours, STransportAdd, STransport, STransferAdd, STransfer, SHotelsAdd, SHotels, SCustomersAdd, SCustomers

async def get_tours_detailed(new_session: AsyncSession) -> list[dict]:
    async with new_session() as session:
            tours = await session.execute(select(Tours))
            tours = tours.scalars().all()
            result = []
            
            for tour in tours:
                tour_dict = {
                    'id': tour.id,
                    'name': tour.name,
                    'description': tour.description,
                    'transfer':None,
                    'transport':None,
                    'total_cost': None,
                    'hotel': None
                }
                
                # Fetch related hotel if hotels_id exists
                if tour.hotels_id:
                    hotel = await session.execute(select(Hotels).where(Hotels.id == tour.hotels_id))
                    hotel = hotel.scalar_one_or_none()
                    if hotel:
                        tour_dict['hotel'] = {
                            'id': hotel.id,
                            'name': hotel.name,
                            'location': hotel.location,
                            'rating': hotel.rating,
                            'price': hotel.price,
                            'description': hotel.description
                        }
                # Fetch related transport if transport_id exists
                if tour.transport_id:
                    transport = await session.execute(select(Transportations).where(Transportations.id == tour.transport_id))
                    transport = transport.scalar_one_or_none()
                    if transport:
                        tour_dict['transport'] = {
                            'id': transport.id,
                            'type': transport.type,
                            'company': transport.company,
                            'price': transport.price,
                            'from_to': transport.from_location + " to " + transport.to_location,
                            'dates': str(transport.from_date) + " - " + str(transport.to_date)
                        }
                # Fetch related transfer if transfer_id exists
                if tour.transfer_id:
                    transfer = await session.execute(select(Transfers).where(Transfers.id == tour.transfer_id))
                    transfer = transfer.scalar_one_or_none()
                    if transfer:
                        tour_dict['transfer'] = {
                            'id': transfer.id,
                            'type': transfer.type,
                            'price': transfer.price,
                        }
                tour_dict['total_cost'] = sum([hotel.price,transport.price,transfer.price])
                
                result.append(tour_dict)
    return result


async def add_transport(transport: STransportAdd, new_session: AsyncSession) -> Transportations:
    async with new_session() as session:
        new_transport = Transportations(
            type=transport.type,
            company=transport.company,
            price=transport.price,
            from_location=transport.from_location,
            to_location=transport.to_location,
            from_date=transport.from_date,
            to_date=transport.to_date
        )
        session.add(new_transport)
        await session.commit()
        await session.refresh(new_transport)
        return new_transport
    

async def add_transfer(transfer: STransferAdd, new_session: AsyncSession) -> Transfers:
    async with new_session() as session:
        new_transfer = Transfers(
            type=transfer.type,
            price=transfer.price
        )
        session.add(new_transfer)
        await session.commit()
        await session.refresh(new_transfer)
        return new_transfer
    
    
async def add_hotel(hotel: SHotelsAdd, new_session: AsyncSession) -> Hotels:
    async with new_session() as session:
        new_hotel = Hotels(
            name=hotel.name,
            location=hotel.location,
            rating=hotel.rating,
            price=hotel.price,
            description=hotel.description
        )
        session.add(new_hotel)
        await session.commit()
        await session.refresh(new_hotel)
        return new_hotel
    

async def add_tour(tour: SToursAdd, new_session: AsyncSession) -> Tours:
    async with new_session() as session:
        new_tour = Tours(
            name=tour.name,
            description=tour.description,
            transfer_id=tour.transfer_id,
            hotels_id=tour.hotels_id,
            transport_id=tour.transport_id
        )
        session.add(new_tour)
        await session.commit()
        await session.refresh(new_tour)
        return new_tour