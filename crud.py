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
from schemas import (
    SToursAdd,
    STours,
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


async def add_transport(
    transport: STransportAdd,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Transportations:
    """Add a new transportation to the database"""
    new_transport = Transportations(**transport.model_dump())
    session.add(new_transport)
    await session.flush()
    return new_transport


async def get_transports(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Transportations]:
    """Fetch all transportations"""
    transports = await session.execute(select(Transportations))
    return transports.scalars().all()


async def add_transfer(
    transfer: STransferAdd,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Transfers:
    """Add a new transfer to the database"""
    new_transfer = Transfers(**transfer.model_dump())
    session.add(new_transfer)
    await session.flush()
    return new_transfer


async def get_transfers(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Transfers]:
    """Fetch all transfers"""
    transfers = await session.execute(select(Transfers))
    return transfers.scalars().all()


async def add_customer(
    customer: SCustomersAdd,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Customers:
    """Add a new customer to the database"""
    new_customer = Customers(**customer.model_dump())
    session.add(new_customer)
    await session.flush()
    await session.refresh(new_customer)
    return new_customer


async def get_customers(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Customers]:
    """Fetch all customers"""
    customers = await session.execute(select(Customers))
    return customers.scalars().all()


async def add_order(
    order: SOrdersAdd, session: AsyncSession = Depends(db_helper.session_dependency)
) -> Orders:
    """Add a new order to the database"""
    new_order = Orders(**order.model_dump())
    session.add(new_order)
    await session.flush()
    return new_order


async def get_orders(
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[Orders]:
    """Fetch all orders"""
    orders = await session.execute(select(Orders))
    return orders.scalars().all()


async def update_order(
    order_id: int,
    order: SOrdersAdd,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> Orders | None:
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


async def get_customer_by_email_password(
    email: str,
    password: str,
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> dict | None:
    """Fetch a customer by email and password for login verification"""
    customer = await session.execute(select(Customers).where(Customers.email == email))
    customer = customer.scalar_one_or_none()

    if customer and customer.password == password:
        return {
            "id": customer.id,
            "name": customer.name,
            "surname": customer.surname,
            "email": customer.email,
            "status": customer.status,
            "phone": customer.phone,
        }
    return None


async def get_customer_by_id(
    customer_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
) -> dict | None:
    """Fetch a customer by ID"""
    customer = await session.execute(
        select(Customers).where(Customers.id == customer_id)
    )
    customer = customer.scalar_one_or_none()

    if customer:
        return {
            "id": customer.id,
            "name": customer.name,
            "surname": customer.surname,
            "email": customer.email,
            "status": customer.status,
            "phone": customer.phone,
        }
    return None
