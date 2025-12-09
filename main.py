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

@app.get("/addtour/")
async def add_tour_page(request: Request):
    """Display the add tour form with available hotels, transfers, and transportations"""
    async with new_session() as session:
        # Fetch hotels
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
        
        # Fetch transfers
        transfers = await session.execute(select(Transfers))
        transfers_list = [
            {
                'id': transfer.id,
                'type': transfer.type,
                'price': transfer.price
            }
            for transfer in transfers.scalars().all()
        ]
        
        # Fetch transportations
        transportations = await session.execute(select(Transportations))
        transportations_list = [
            {
                'id': transportation.id,
                'company': transportation.company,
                'type': transportation.type,
                'price': transportation.price,
                'from_location': transportation.from_location,
                'to_location': transportation.to_location
            }
            for transportation in transportations.scalars().all()
        ]
    
    return templates.TemplateResponse('addtour.html', {
        "request": request,
        "hotels": hotels_list,
        "transfers": transfers_list,
        "transportations": transportations_list
    })

@app.post("/addtour/")
async def create_tour(request: Request):
    """Handle form submission to create a new tour. Allows creating transfer/transportation on the fly."""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    # Existing selections (ids) if chosen
    transfer_id = to_int(form_data.get('transfer_id'))
    transport_id = to_int(form_data.get('transport_id'))

    # New transfer fields
    new_transfer_type = (form_data.get('new_transfer_type') or "").strip()
    new_transfer_price = to_int(form_data.get('new_transfer_price'))

    # New transportation fields
    new_transport_company = (form_data.get('new_transport_company') or "").strip()
    new_transport_type = (form_data.get('new_transport_type') or "").strip()
    new_transport_price = to_int(form_data.get('new_transport_price'))
    new_transport_from = (form_data.get('new_transport_from') or "").strip()
    new_transport_to = (form_data.get('new_transport_to') or "").strip()
    new_transport_from_date = (form_data.get('new_transport_from_date') or "").strip()
    new_transport_to_date = (form_data.get('new_transport_to_date') or "").strip()

    async with new_session() as session:
        try:
            # Create transfer if no id provided but new data given
            if not transfer_id and (new_transfer_type or new_transfer_price is not None):
                new_transfer = Transfers(
                    type=new_transfer_type or None,
                    price=new_transfer_price
                )
                session.add(new_transfer)
                await session.flush()
                transfer_id = new_transfer.id

            # Create transportation if no id provided but new data given
            if not transport_id and (
                new_transport_company or new_transport_type or new_transport_price is not None or
                new_transport_from or new_transport_to or new_transport_from_date or new_transport_to_date
            ):
                new_transport = Transportations(
                    company=new_transport_company or None,
                    type=new_transport_type or None,
                    price=new_transport_price,
                    from_location=new_transport_from or None,
                    to_location=new_transport_to or None,
                    from_date=new_transport_from_date or None,
                    to_date=new_transport_to_date or None
                )
                session.add(new_transport)
                await session.flush()
                transport_id = new_transport.id

            # Parse tour data and create tour
            tour = Tours(
                name=form_data.get('name'),
                description=form_data.get('description') or None,
                transfer_id=transfer_id,
                hotels_id=to_int(form_data.get('hotels_id')),
                transport_id=transport_id,
            )
            session.add(tour)
            await session.flush()
            await session.commit()

            # Fetch hotels, transfers, and transportations for response
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

            transfers = await session.execute(select(Transfers))
            transfers_list = [
                {
                    'id': transfer.id,
                    'type': transfer.type,
                    'price': transfer.price
                }
                for transfer in transfers.scalars().all()
            ]

            transportations = await session.execute(select(Transportations))
            transportations_list = [
                {
                    'id': transportation.id,
                    'company': transportation.company,
                    'type': transportation.type,
                    'price': transportation.price,
                    'from_location': transportation.from_location,
                    'to_location': transportation.to_location
                }
                for transportation in transportations.scalars().all()
            ]

            return templates.TemplateResponse('addtour.html', {
                "request": request,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "success": "Tour created successfully! 🎉",
                "success_show": True
            })
        except Exception as e:
            # Fetch all data for response on error
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

            transfers = await session.execute(select(Transfers))
            transfers_list = [
                {
                    'id': transfer.id,
                    'type': transfer.type,
                    'price': transfer.price
                }
                for transfer in transfers.scalars().all()
            ]

            transportations = await session.execute(select(Transportations))
            transportations_list = [
                {
                    'id': transportation.id,
                    'company': transportation.company,
                    'type': transportation.type,
                    'price': transportation.price,
                    'from_location': transportation.from_location,
                    'to_location': transportation.to_location
                }
                for transportation in transportations.scalars().all()
            ]

            return templates.TemplateResponse('addtour.html', {
                "request": request,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "error": f"Error creating tour: {str(e)}",
                "error_show": True
            })
        

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

@app.get("/hotel/{hotel_id}")
async def read_hotel(request: Request, hotel_id: int):
    async with new_session() as session:
        hotel = await session.execute(select(Hotels).where(Hotels.id == hotel_id))
        hotel = hotel.scalar_one_or_none()
        if hotel:
            result = {
                'id': hotel.id,
                'name': hotel.name,
                'location': hotel.location,
                'rating': hotel.rating,
                'price': hotel.price,
                'description': hotel.description
            }
            return templates.TemplateResponse('hotel.html', {"request": request, "hotel": result})
        else:
            return {"error": "Hotel not found"}

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


        
if __name__ == "__main__":
    
    uvicorn.run("main:app", reload=True)