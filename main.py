from fastapi import FastAPI,Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from schemas import SToursAdd, STours
from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,Transfers,async_sessionmaker,new_session
from sqlalchemy import select
import uvicorn

templates = Jinja2Templates(directory="templates")

app = FastAPI()



@app.get("/")
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

@app.post("/addtour")
async def create_tour(request: Request):
    form_data = await request.form()
    
    # Parse form data
    tour_data = {
        'name': form_data.get('name'),
        'description': form_data.get('description') or None,
        'transfer_id': int(form_data.get('transfer_id')) if form_data.get('transfer_id') else None,
        'hotels_id': int(form_data.get('hotels_id')) if form_data.get('hotels_id') else None,
        'transport_id': int(form_data.get('transport_id')) if form_data.get('transport_id') else None,
        'total_cost': float(form_data.get('total_cost')) if form_data.get('total_cost') else None,
    }
    
    async with new_session() as session:
        try:
            # Create tour
            tour = Tours(**tour_data)
            session.add(tour)
            await session.flush()
            await session.commit()
            
            # Fetch hotels for response
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
            
            return templates.TemplateResponse('index.html', {
                "request": request, 
                "hotels": hotels_list,
                "success": "Tour created successfully! 🎉",
                "success_show": True
            })
        except Exception as e:
            # Fetch hotels for response
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
            
            return templates.TemplateResponse('index.html', {
                "request": request, 
                "hotels": hotels_list,
                "error": f"Error creating tour: {str(e)}",
                "error_show": True
            })
        
if __name__ == "__main__":
    
    uvicorn.run("main:app", reload=True)