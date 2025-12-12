from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from fastapi import APIRouter
from database import (
    Tours,
    Customers,
    Orders,
    Managers,
    Hotels,
    Transportations,
    Transfers,
    new_session,
)
from sqlalchemy import select
from hotel.crud import (
    
    add_hotel,
   
    get_hotels,
    
)

from schemas import (
    
    SHotelsAdd,
    
)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/hotel/{hotel_id}")
async def read_hotel(request: Request, hotel_id: int):
    async with new_session() as session:
        hotel = await session.execute(select(Hotels).where(Hotels.id == hotel_id))
        hotel = hotel.scalar_one_or_none()
        if hotel:

            return templates.TemplateResponse(
                "hotel.html", {"request": request, "hotel": hotel}
            )
        else:
            return {"error": "Hotel not found"}


@app.get("/hotels/")
async def read_hotels():
    async with new_session() as session:
        hotels = await session.execute(select(Hotels))
        hotels = hotels.scalars().all()

    return hotels

@app.get("/addhotel/")
async def add_hotel_page(request: Request):
    """Display the add hotel form"""
    return templates.TemplateResponse("addhotel.html", {"request": request})


@app.post("/addhotel/")
async def create_hotel(request: Request):
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

        await add_hotel(hotel_schema, new_session)

        # Redirect back to previous page or tour form
        referer = request.headers.get("referer", "/")
        return RedirectResponse(url=referer, status_code=303)

    except Exception as e:
        return templates.TemplateResponse(
            "addhotel.html",
            {
                "request": request,
                "error": f"Error creating hotel: {str(e)}",
                "error_show": True,
            },
        )