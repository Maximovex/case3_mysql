from fastapi import FastAPI,Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from schemas import SToursAdd, STours
from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,async_sessionmaker,new_session
from sqlalchemy import select
import os

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
async def read_root(request: Request):
    async with new_session() as session:
        hotels = await session.execute(select(Hotels))
        hotels_list = [
            {
                'id': hotel.id,
                'name': hotel.name,
                'location': hotel.location,
                'rating': hotel.rating,
                'price': hotel.price
            }
            for hotel in hotels.scalars().all()
        ]
    return templates.TemplateResponse('index.html', {"request": request, "hotels": hotels_list})

@app.get("/tours/")
async def tours_page(request: Request):
    async with new_session() as session:
        tours = await session.execute(select(Tours))
        tours = tours.scalars().all()
        result = []
        
        for tour in tours:
            tour_dict = {
                'id': tour.id,
                'name': tour.name,
                'description': tour.description,
                'transfer_id': tour.transfer_id,
                'hotels_id': tour.hotels_id,
                'transport_id': tour.transport_id,
                'total_cost': tour.total_cost,
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
            
            result.append(tour_dict)
    
    return templates.TemplateResponse('tours.html', {"request": request, "tours": result})

@app.get("/orders/")
async def read_orders():
    async with new_session() as session:
        orders = await session.execute(select(Orders))
        return orders.scalars().all()
    
@app.get("/customers/")
async def read_customers():
    async with new_session() as session:
        customers = await session.execute(select(Customers))
        return customers.scalars().all()

@app.get("/managers/")
async def read_managers():
    async with new_session() as session:
        managers = await session.execute(select(Managers))
        return managers.scalars().all()


@app.get("/hotels/")
async def read_hotels():
    async with new_session() as session:
        hotels = await session.execute(select(Hotels))
        result = []
        for hotel in hotels.scalars().all():
            hotel_dict = {
                'id': hotel.id,
                'name': hotel.name,
                'location': hotel.location,
                'rating': hotel.rating,
                'price': hotel.price,
                'description': hotel.description
            }
            result.append(hotel_dict)
    return result

@app.post("/tours/")
async def create_tour(data: SToursAdd=Depends()):
    async with new_session() as session:
        tour_dict=data.model_dump()
        tour = Tours(**tour_dict)
        session.add(tour)
        await session.flush()
        await session.commit()
    return tour