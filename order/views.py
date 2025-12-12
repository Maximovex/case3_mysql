from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_helper import db_helper
from database import Orders
from starlette.templating import Jinja2Templates
from schemas import SOrders,SOrdersAdd,STours

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["orders"])

@router.get("/")
async def read_orders(
    request: Request, 
    session: AsyncSession = Depends(db_helper.session_dependency)
):
    orders = await session.execute(select(Orders))
    orders_list = orders.scalars().all()
    return templates.TemplateResponse(
        "order.html", {"request": request, "orders": orders_list}
    )