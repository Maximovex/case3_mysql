from db_helper import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Customers
from schemas import SCustomers


async def get_customers(
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> list[SCustomers]:
    """Fetch all customers from the database"""
    customers = await session.execute(select(Customers))
    customers = customers.scalars().all()
    return [SCustomers.model_validate(customer) for customer in customers]

async def get_customer_by_id(
    customer_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
) -> SCustomers | None:
    """Fetch a customer by ID"""
    customer = await session.execute(
        select(Customers).where(Customers.id == customer_id)
    )
    customer = customer.scalar_one_or_none()

    if customer:
       return SCustomers.model_validate(customer)
    return None