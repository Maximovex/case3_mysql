from db_helper import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Orders
from schemas import SOrders, STours, SCustomers, SManagers
from dependencies import (
    get_tours_dependency,
    get_managers_dependency,
    get_customers_dependency,
)


async def get_orders(
    tours: list[STours] = Depends(get_tours_dependency),
    managers: list[SManagers] = Depends(get_managers_dependency),
    customers: list[SCustomers] = Depends(get_customers_dependency),
    session: AsyncSession = Depends(db_helper.session_dependency),
) -> list[SOrders]:
    """Fetch all orders from the database"""
    orders = await session.execute(select(Orders))
    orders = orders.scalars().all()
    orders_schemas = [SOrders.model_validate(order) for order in orders]
    for order_schema in orders_schemas:
        if order_schema.tour_id:
            for tour in tours:
                if tour.id == order_schema.tour_id:
                    order_schema.tour = tour
                    break
        if order_schema.manager_id:
            for mgr in managers:
                if mgr.id == order_schema.manager_id:
                    order_schema.manager = mgr
                    break
        if order_schema.customer_id:
            for cust in customers:
                if cust.id == order_schema.customer_id:
                    order_schema.customer = cust
                    break
        order_schema.total_amount = order_schema.tour.total_cost if order_schema.tour else 0
    return orders_schemas
