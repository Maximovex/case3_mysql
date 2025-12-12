from sqlalchemy import select
from database import Base, Tours, Customers, Orders, Managers, Transfers, Hotels, Transportations, new_session, AsyncSession
from schemas import SToursAdd, STours, STransportAdd, STransport, STransferAdd, STransfer, SHotelsAdd, SHotels, SCustomersAdd, SCustomers, SOrdersAdd

async def get_tours_detailed(new_session_factory: AsyncSession) -> list[dict]:
    """Fetch all tours with related hotel, transfer, and transportation details"""
    async with new_session_factory() as session:
        tours = await session.execute(select(Tours))
        tours = tours.scalars().all()
        result = []
        
        for tour in tours:
            tour_dict = {
                'id': tour.id,
                'name': tour.name,
                'description': tour.description,
                'transfer': None,
                'transport': None,
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
            
            # Calculate total cost safely
            prices = [
                tour_dict['hotel']['price'] if tour_dict['hotel'] else 0,
                tour_dict['transport']['price'] if tour_dict['transport'] else 0,
                tour_dict['transfer']['price'] if tour_dict['transfer'] else 0
            ]
            tour_dict['total_cost'] = sum([p for p in prices if p is not None])
            
            result.append(tour_dict)
    return result

async def add_tour(tour: SToursAdd, session: AsyncSession) -> Tours:
    """Add a new tour to the database"""
    new_tour = Tours(**tour.model_dump())
    session.add(new_tour)
    await session.flush()
    return new_tour

async def add_transport(transport: STransportAdd, session: AsyncSession) -> Transportations:
    """Add a new transportation to the database"""
    new_transport = Transportations(**transport.model_dump())
    session.add(new_transport)
    await session.flush()
    return new_transport

async def get_transports(new_session_factory: AsyncSession) -> list[Transportations]:
    """Fetch all transportations"""
    async with new_session_factory() as session:
        transports = await session.execute(select(Transportations))
        return transports.scalars().all()

async def add_transfer(transfer: STransferAdd, session: AsyncSession) -> Transfers:
    """Add a new transfer to the database"""
    new_transfer = Transfers(**transfer.model_dump())
    session.add(new_transfer)
    await session.flush()
    return new_transfer

async def get_transfers(new_session_factory: AsyncSession) -> list[Transfers]:
    """Fetch all transfers"""
    async with new_session_factory() as session:
        transfers = await session.execute(select(Transfers))
        return transfers.scalars().all()

async def add_hotel(hotel: SHotelsAdd, new_session_factory: AsyncSession) -> Hotels:
    """Add a new hotel to the database"""
    async with new_session_factory() as session:
        new_hotel = Hotels(**hotel.model_dump())
        session.add(new_hotel)
        await session.flush()
        
        return new_hotel

async def get_hotels(new_session_factory: AsyncSession) -> list[Hotels]:
    """Fetch all hotels"""
    async with new_session_factory() as session:
        hotels = await session.execute(select(Hotels))
        return hotels.scalars().all()

async def add_customer(customer: SCustomersAdd, new_session_factory: AsyncSession) -> Customers:
    """Add a new customer to the database"""
    async with new_session_factory() as session:
        new_customer = Customers(**customer.model_dump())
        session.add(new_customer)
        await session.commit()
        await session.refresh(new_customer)
        return new_customer

async def get_customers(new_session_factory: AsyncSession) -> list[Customers]:
    """Fetch all customers"""
    async with new_session_factory() as session:
        customers = await session.execute(select(Customers))
        return customers.scalars().all()

async def get_tour_by_id(tour_id: int, new_session_factory: AsyncSession) -> dict | None:
    """Fetch a single tour with all related data"""
    async with new_session_factory() as session:
        tour = await session.execute(select(Tours).where(Tours.id == tour_id))
        tour = tour.scalar_one_or_none()
        
        if not tour:
            return None
        
        tour_dict = {
            'id': tour.id,
            'name': tour.name,
            'description': tour.description,
            'hotels_id': tour.hotels_id,
            'transfer_id': tour.transfer_id,
            'transport_id': tour.transport_id,
            'transfer': None,
            'transport': None,
            'hotel': None
        }
        
        # Fetch related hotel
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
        
        # Fetch related transport
        if tour.transport_id:
            transport = await session.execute(select(Transportations).where(Transportations.id == tour.transport_id))
            transport = transport.scalar_one_or_none()
            if transport:
                tour_dict['transport'] = {
                    'id': transport.id,
                    'type': transport.type,
                    'company': transport.company,
                    'price': transport.price,
                    'from_location': transport.from_location,
                    'to_location': transport.to_location,
                    'from_date': transport.from_date,
                    'to_date': transport.to_date,
                    'from_to': f"{transport.from_location} to {transport.to_location}",
                    'dates': f"{transport.from_date} - {transport.to_date}"
                }
        
        # Fetch related transfer
        if tour.transfer_id:
            transfer = await session.execute(select(Transfers).where(Transfers.id == tour.transfer_id))
            transfer = transfer.scalar_one_or_none()
            if transfer:
                tour_dict['transfer'] = {
                    'id': transfer.id,
                    'type': transfer.type,
                    'price': transfer.price,
                }
        
        return tour_dict

async def update_tour(tour_id: int, tour: SToursAdd, session: AsyncSession) -> Tours | None:
    """Update an existing tour"""
    tour_obj = await session.execute(select(Tours).where(Tours.id == tour_id))
    tour_obj = tour_obj.scalar_one_or_none()
    
    if not tour_obj:
        return None
    
    # Update fields
    tour_obj.name = tour.name
    tour_obj.description = tour.description
    tour_obj.transfer_id = tour.transfer_id
    tour_obj.hotels_id = tour.hotels_id
    tour_obj.transport_id = tour.transport_id
    
    session.add(tour_obj)
    await session.flush()
    return tour_obj

async def delete_tour(tour_id: int, new_session_factory: AsyncSession) -> bool:
    """Delete a tour"""
    async with new_session_factory() as session:
        tour = await session.execute(select(Tours).where(Tours.id == tour_id))
        tour = tour.scalar_one_or_none()
        
        if not tour:
            return False
        
        await session.delete(tour)
        await session.commit()
        return True
    
async def add_order(order: SOrdersAdd, session: AsyncSession) -> Orders:
    """Add a new order to the database"""
    new_order = Orders(**order.model_dump())
    session.add(new_order)
    await session.flush()
    return new_order

async def get_orders(new_session_factory: AsyncSession) -> list[Orders]:
    """Fetch all orders"""
    async with new_session_factory() as session:
        orders = await session.execute(select(Orders))
        return orders.scalars().all()  
    
async def update_order(order_id: int, order: SOrdersAdd, session: AsyncSession) -> Orders | None:
    """Update an existing order"""
    order_obj = await session.execute(select(Orders).where(Orders.id == order_id))
    order_obj = order_obj.scalar_one_or_none()
    
    if not order_obj:
        return None
    
    # Update fields
    order_obj.order_date = order.order_date
    order_obj.customer_id = order.customer_id
    order_obj.tour_id = order.tour_id
    order_obj.total_amount = order.total_amount
    order_obj.payment_status = order.payment_status
    order_obj.manager_id = order.manager_id
    
    session.add(order_obj)
    await session.flush()
    return order_obj

async def get_customer_by_email_password(email: str, password: str, new_session_factory: AsyncSession) -> dict | None:
    """Fetch a customer by email and password for login verification"""
    async with new_session_factory() as session:
        customer = await session.execute(select(Customers).where(Customers.email == email))
        customer = customer.scalar_one_or_none()
        
        if customer and customer.password == password:
            return {
                'id': customer.id,
                'name': customer.name,
                'surname': customer.surname,
                'email': customer.email,
                'status': customer.status,
                'phone': customer.phone
            }
        return None
    
async def get_customer_by_id(customer_id: int, new_session_factory: AsyncSession) -> dict | None:
    """Fetch a customer by ID"""
    async with new_session_factory() as session:
        customer = await session.execute(select(Customers).where(Customers.id == customer_id))
        customer = customer.scalar_one_or_none()
        
        if customer:
            return {
                'id': customer.id,
                'name': customer.name,
                'surname': customer.surname,
                'email': customer.email,
                'status': customer.status,
                'phone': customer.phone
            }
        return None