from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession
from db_helper import db_helper
from fastapi import APIRouter, Request, Depends
from database import (
    Tours,
    Customers,
    Orders,
    Managers,
    Hotels,
    Transportations,
    Transfers,
)
from dependencies import (
    get_hotels_dependency,get_hotel_by_id_dependency,
)
from sqlalchemy import select
from hotel.crud import (
    add_hotel,
    get_hotels,
)

from schemas import (
    SHotelsAdd,
    SHotels,
)

router = APIRouter(tags=["hotel"])
templates = Jinja2Templates(directory="templates")


@router.get("/{hotel_id}", response_model=SHotels)
async def read_hotel(
    request: Request,
    hotel_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    hotel = await session.execute(select(Hotels).where(Hotels.id == hotel_id))
    hotel = hotel.scalar_one_or_none()
    if hotel:
        return templates.TemplateResponse(
            "hotel.html", {"request": request, "hotel": hotel}
        )
    else:
        return {"error": "Hotel not found"}


@router.get("/", response_model=list[SHotels])
async def read_hotels(
    request: Request, hotels: list[SHotels] = Depends(get_hotels_dependency)
):
    return templates.TemplateResponse(
        "hotel.html", {"request": request, "hotels": hotels}
    )


@router.get("/add/")
async def add_hotel_page(request: Request):
    """Display the add hotel form"""
    return templates.TemplateResponse("addhotel.html", {"request": request})


@router.post("/add/")
async def create_hotel(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Handle hotel creation form submission"""
    from fastapi.responses import RedirectResponse

    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    try:
        hotel_schema = SHotelsAdd(
            name=form_data.get("name"),
            location=form_data.get("location"),
            rating=to_int(form_data.get("rating")),
            price=to_int(form_data.get("price")),
            description=form_data.get("description") or None,
        )

        newhotel = await add_hotel(hotel_schema, session)
        await session.commit()

        # Show success message and allow adding another hotel
        return templates.TemplateResponse(
            "addhotel.html",
            {
                "request": request,
                "success": f"Hotel '{newhotel.name}' has been successfully added!",
                "success_show": True,
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            "addhotel.html",
            {
                "request": request,
                "error": f"Error creating hotel: {str(e)}",
                "error_show": True,
            },
        )

@router.patch("/{hotel_id}/update/", response_model=SHotels)
async def update_hotel(
    hotel_id: int,
    hotel_update: SHotelsAdd=Depends(),
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Update an existing hotel"""
    hotel = await get_hotel_by_id_dependency(hotel_id, session)
    if not hotel:
        return {"error": "Hotel not found"}

    for key, value in hotel_update.model_dump().items():
        setattr(hotel, key, value)

    session.add(hotel)
    await session.commit()
    await session.refresh(hotel)

    return hotel

@router.delete("/{hotel_id}/delete/")
async def delete_hotel(
    hotel_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Delete a hotel"""
    hotel = await get_hotel_by_id_dependency(hotel_id, session)
    if not hotel:
        return {"error": "Hotel not found"}

    await session.delete(hotel)
    await session.commit()

    return {"success": f"Hotel with ID {hotel_id} has been deleted."}