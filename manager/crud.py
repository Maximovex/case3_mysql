from db_helper import db_helper
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Orders,Managers
from schemas import SOrders,SManagers

async def get_managers(
    session: AsyncSession = Depends(db_helper.session_dependency)
) -> list[SManagers]:
    """Fetch all managers"""
    managers = await session.execute(select(Managers))
    managers = managers.scalars().all()
    return [SManagers.model_validate(manager) for manager in managers]

async def get_manager_by_id(
    manager_id: int, session: AsyncSession = Depends(db_helper.session_dependency)
) -> SManagers | None:
    """Fetch a manager by ID"""
    manager = await session.execute(
        select(Managers).where(Managers.id == manager_id)
    )
    manager = manager.scalar_one_or_none()

    if manager:
        return SManagers.model_validate(manager)
    return None