from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from database import Tours, Customers, Orders, Managers, Hotels, Transportations,Transfers,new_session
from sqlalchemy import select
from crud import get_tours_detailed,add_hotel,add_transport,add_transfer,add_tour,get_hotels,get_transfers,get_transports,get_tour_by_id,update_tour,delete_tour
from schemas import SToursAdd, STours, STransportAdd, STransport, STransferAdd, STransfer, SHotelsAdd, SHotels, SCustomersAdd, SCustomers
import uvicorn

templates = Jinja2Templates(directory="templates")

app = FastAPI()



@app.get("/")
async def tours_page(request: Request):
    result = await get_tours_detailed(new_session)
    
    return templates.TemplateResponse('tours.html', {"request": request, "tours": result})

@app.get("/addtour/")
async def add_tour_page(request: Request):
    """Display the add tour form with available hotels, transfers, and transportations"""
    hotels_list = await get_hotels(new_session)
    transfers_list = await get_transfers(new_session)
    transportations_list = await get_transports(new_session)
    
    # Convert ORM objects to dictionaries for template
    hotels_data = [
        {
            'id': h.id,
            'name': h.name,
            'location': h.location,
            'rating': h.rating,
            'price': h.price
        }
        for h in hotels_list
    ]
    
    transfers_data = [
        {
            'id': t.id,
            'type': t.type,
            'price': t.price
        }
        for t in transfers_list
    ]
    
    transportations_data = [
        {
            'id': tr.id,
            'company': tr.company,
            'type': tr.type,
            'price': tr.price,
            'from_location': tr.from_location,
            'to_location': tr.to_location
        }
        for tr in transportations_list
    ]

    return templates.TemplateResponse('addtour.html', {
        "request": request,
        "hotels": hotels_data,
        "transfers": transfers_data,
        "transportations": transportations_data
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
                transfer_schema = STransferAdd(
                    type=new_transfer_type or "Unknown",
                    price=new_transfer_price
                )
                created_transfer = await add_transfer(transfer_schema, session)
                transfer_id = created_transfer.id

            # Create transportation if no id provided but new data given
            if not transport_id and (
                new_transport_company or new_transport_type or new_transport_price is not None or
                new_transport_from or new_transport_to or new_transport_from_date or new_transport_to_date
            ):
                transport_schema = STransportAdd(
                    company=new_transport_company or "Unknown",
                    type=new_transport_type or "Unknown",
                    price=new_transport_price,
                    from_location=new_transport_from or None,
                    to_location=new_transport_to or None,
                    from_date=new_transport_from_date or None,
                    to_date=new_transport_to_date or None
                )
                created_transport = await add_transport(transport_schema, session)
                transport_id = created_transport.id

            # Create tour using schema
            tour_schema = SToursAdd(
                name=form_data.get('name'),
                description=form_data.get('description') or None,
                transfer_id=transfer_id,
                hotels_id=to_int(form_data.get('hotels_id')),
                transport_id=transport_id,
            )
            await add_tour(tour_schema, session)
            await session.commit()

            # Fetch fresh data for response
            hotels_list = await get_hotels(new_session)
            transfers_list = await get_transfers(new_session)
            transportations_list = await get_transports(new_session)

            # Convert to dictionaries
            hotels_data = [
                {
                    'id': h.id,
                    'name': h.name,
                    'location': h.location,
                    'rating': h.rating,
                    'price': h.price
                }
                for h in hotels_list
            ]
            
            transfers_data = [
                {
                    'id': t.id,
                    'type': t.type,
                    'price': t.price
                }
                for t in transfers_list
            ]
            
            transportations_data = [
                {
                    'id': tr.id,
                    'company': tr.company,
                    'type': tr.type,
                    'price': tr.price,
                    'from_location': tr.from_location,
                    'to_location': tr.to_location
                }
                for tr in transportations_list
            ]

            return templates.TemplateResponse('addtour.html', {
                "request": request,
                "hotels": hotels_data,
                "transfers": transfers_data,
                "transportations": transportations_data,
                "success": "Tour created successfully! 🎉",
                "success_show": True
            })
        except Exception as e:
            await session.rollback()
            
            # Fetch fresh data for error response
            hotels_list = await get_hotels(new_session)
            transfers_list = await get_transfers(new_session)
            transportations_list = await get_transports(new_session)

            hotels_data = [
                {
                    'id': h.id,
                    'name': h.name,
                    'location': h.location,
                    'rating': h.rating,
                    'price': h.price
                }
                for h in hotels_list
            ]
            
            transfers_data = [
                {
                    'id': t.id,
                    'type': t.type,
                    'price': t.price
                }
                for t in transfers_list
            ]
            
            transportations_data = [
                {
                    'id': tr.id,
                    'company': tr.company,
                    'type': tr.type,
                    'price': tr.price,
                    'from_location': tr.from_location,
                    'to_location': tr.to_location
                }
                for tr in transportations_list
            ]

            return templates.TemplateResponse('addtour.html', {
                "request": request,
                "hotels": hotels_data,
                "transfers": transfers_data,
                "transportations": transportations_data,
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

@app.get("/update-tours/")
async def update_tours_page(request: Request):
    """Display list of tours for updating"""
    result = await get_tours_detailed(new_session)
    return templates.TemplateResponse('update_tours.html', {"request": request, "tours": result})

@app.get("/tour/{tour_id}")
async def tour_page(request: Request, tour_id: int):
    """Display tour details and update form"""
    tour = await get_tour_by_id(tour_id, new_session)
    
    if not tour:
        return templates.TemplateResponse('tour.html', {
            "request": request,
            "tour": None
        })
    
    hotels_list = await get_hotels(new_session)
    transfers_list = await get_transfers(new_session)
    transportations_list = await get_transports(new_session)
    
    # Convert ORM objects to dictionaries
    hotels_data = [
        {
            'id': h.id,
            'name': h.name,
            'location': h.location,
            'rating': h.rating,
            'price': h.price
        }
        for h in hotels_list
    ]
    
    transfers_data = [
        {
            'id': t.id,
            'type': t.type,
            'price': t.price
        }
        for t in transfers_list
    ]
    
    transportations_data = [
        {
            'id': tr.id,
            'company': tr.company,
            'type': tr.type,
            'price': tr.price,
            'from_location': tr.from_location,
            'to_location': tr.to_location
        }
        for tr in transportations_list
    ]
    
    return templates.TemplateResponse('tour.html', {
        "request": request,
        "tour": tour,
        "hotels": hotels_data,
        "transfers": transfers_data,
        "transportations": transportations_data
    })

@app.post("/tour/{tour_id}")
async def update_tour_handler(request: Request, tour_id: int):
    """Handle tour update form submission"""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    # Get existing selection ids
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
                transfer_schema = STransferAdd(
                    type=new_transfer_type or "Unknown",
                    price=new_transfer_price
                )
                created_transfer = await add_transfer(transfer_schema, session)
                transfer_id = created_transfer.id

            # Create transportation if no id provided but new data given
            if not transport_id and (
                new_transport_company or new_transport_type or new_transport_price is not None or
                new_transport_from or new_transport_to or new_transport_from_date or new_transport_to_date
            ):
                transport_schema = STransportAdd(
                    company=new_transport_company or "Unknown",
                    type=new_transport_type or "Unknown",
                    price=new_transport_price,
                    from_location=new_transport_from or None,
                    to_location=new_transport_to or None,
                    from_date=new_transport_from_date or None,
                    to_date=new_transport_to_date or None
                )
                created_transport = await add_transport(transport_schema, session)
                transport_id = created_transport.id

            # Update tour using schema
            tour_schema = SToursAdd(
                name=form_data.get('name'),
                description=form_data.get('description') or None,
                transfer_id=transfer_id,
                hotels_id=to_int(form_data.get('hotels_id')),
                transport_id=transport_id,
            )
            await update_tour(tour_id, tour_schema, session)
            await session.commit()

            # Fetch updated tour data
            tour = await get_tour_by_id(tour_id, new_session)
            hotels_list = await get_hotels(new_session)
            transfers_list = await get_transfers(new_session)
            transportations_list = await get_transports(new_session)

            # Convert to dictionaries
            hotels_data = [
                {
                    'id': h.id,
                    'name': h.name,
                    'location': h.location,
                    'rating': h.rating,
                    'price': h.price
                }
                for h in hotels_list
            ]
            
            transfers_data = [
                {
                    'id': t.id,
                    'type': t.type,
                    'price': t.price
                }
                for t in transfers_list
            ]
            
            transportations_data = [
                {
                    'id': tr.id,
                    'company': tr.company,
                    'type': tr.type,
                    'price': tr.price,
                    'from_location': tr.from_location,
                    'to_location': tr.to_location
                }
                for tr in transportations_list
            ]

            return templates.TemplateResponse('tour.html', {
                "request": request,
                "tour": tour,
                "hotels": hotels_data,
                "transfers": transfers_data,
                "transportations": transportations_data,
                "success": "Tour updated successfully! 🎉",
                "success_show": True
            })
        except Exception as e:
            await session.rollback()
            
            # Fetch tour data for error response
            tour = await get_tour_by_id(tour_id, new_session)
            hotels_list = await get_hotels(new_session)
            transfers_list = await get_transfers(new_session)
            transportations_list = await get_transports(new_session)

            hotels_data = [
                {
                    'id': h.id,
                    'name': h.name,
                    'location': h.location,
                    'rating': h.rating,
                    'price': h.price
                }
                for h in hotels_list
            ]
            
            transfers_data = [
                {
                    'id': t.id,
                    'type': t.type,
                    'price': t.price
                }
                for t in transfers_list
            ]
            
            transportations_data = [
                {
                    'id': tr.id,
                    'company': tr.company,
                    'type': tr.type,
                    'price': tr.price,
                    'from_location': tr.from_location,
                    'to_location': tr.to_location
                }
                for tr in transportations_list
            ]

            return templates.TemplateResponse('tour.html', {
                "request": request,
                "tour": tour,
                "hotels": hotels_data,
                "transfers": transfers_data,
                "transportations": transportations_data,
                "error": f"Error updating tour: {str(e)}",
                "error_show": True
            })

@app.post("/tour/{tour_id}/delete")
async def delete_tour_handler(request: Request, tour_id: int):
    """Handle tour deletion"""
    try:
        success = await delete_tour(tour_id, new_session)
        
        if success:
            # Redirect to update tours page after successful deletion
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url="/update-tours/", status_code=303)
        else:
            # Tour not found
            result = await get_tours_detailed(new_session)
            return templates.TemplateResponse('update_tours.html', {
                "request": request,
                "tours": result,
                "error": "Tour not found",
                "error_show": True
            })
    except Exception as e:
        # Error during deletion
        result = await get_tours_detailed(new_session)
        return templates.TemplateResponse('update_tours.html', {
            "request": request,
            "tours": result,
            "error": f"Error deleting tour: {str(e)}",
            "error_show": True
        })

@app.get("/addhotel/")
async def add_hotel_page(request: Request):
    """Display the add hotel form"""
    return templates.TemplateResponse('addhotel.html', {
        "request": request
    })

@app.post("/addhotel/")
async def create_hotel(request: Request):
    """Handle hotel creation form submission"""
    from fastapi.responses import RedirectResponse
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    try:
        hotel_schema = SHotelsAdd(
            name=form_data.get('name'),
            location=form_data.get('location'),
            rating=to_int(form_data.get('rating')),
            price=to_int(form_data.get('price')),
            description=form_data.get('description') or None
        )
        
        await add_hotel(hotel_schema, new_session)
        
        # Redirect back to previous page or tour form
        referer = request.headers.get('referer', '/')
        return RedirectResponse(url=referer, status_code=303)
        
    except Exception as e:
        return templates.TemplateResponse('addhotel.html', {
            "request": request,
            "error": f"Error creating hotel: {str(e)}",
            "error_show": True
        })

if __name__ == "__main__":
    
    uvicorn.run("main:app", reload=True)