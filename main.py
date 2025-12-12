from fastapi import FastAPI, Depends
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.responses import Response
from database import Tours, Customers, Orders, Managers, Hotels, Transportations,Transfers,new_session
from sqlalchemy import select
from crud import get_customer_by_id, get_tours_detailed,add_hotel,add_transport,add_transfer,add_tour,get_hotels,get_transfers,get_transports,get_tour_by_id,update_tour,delete_tour,add_customer,get_customers,add_order,get_customer_by_email_password
from dependencies import get_hotels_dependency, get_transfers_dependency, get_transports_dependency
from schemas import SToursAdd, STours, STransportAdd, STransport, STransferAdd, STransfer, SHotelsAdd, SHotels, SCustomersAdd, SCustomers, SOrdersAdd
import uvicorn
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

templates = Jinja2Templates(directory="templates")

app = FastAPI()





@app.get("/")
async def tours_page(request: Request):
    result = await get_tours_detailed(new_session)
    
    return templates.TemplateResponse('tours.html', {"request": request, "tours": result})

@app.get("/addtour/")
async def add_tour_page(
    request: Request,
    hotels_list: list[Hotels] = Depends(get_hotels_dependency),
    transfers_list: list[Transfers] = Depends(get_transfers_dependency),
    transportations_list: list[Transportations] = Depends(get_transports_dependency)
):
    """Display the add tour form with available hotels, transfers, and transportations"""
    
    
    
   
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

            
            
            

            return templates.TemplateResponse('addtour.html', {
                "request": request,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "success": "Tour created successfully! 🎉",
                "success_show": True
            })
        except Exception as e:
            await session.rollback()
            
            # Fetch fresh data for error response
            hotels_list = await get_hotels(new_session)
            transfers_list = await get_transfers(new_session)
            transportations_list = await get_transports(new_session)

            
            
            

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
   
    
    return templates.TemplateResponse('tour.html', {
        "request": request,
        "tour": tour,
        "hotels": hotels_list,
        "transfers": transfers_list,
        "transportations": transportations_list
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


            return templates.TemplateResponse('tour.html', {
                "request": request,
                "tour": tour,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
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

            

            return templates.TemplateResponse('tour.html', {
                "request": request,
                "tour": tour,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
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

@app.get("/register/")
async def register_page(request: Request):
    """Display customer registration form"""
    return templates.TemplateResponse('registration.html', {
        "request": request
    })

@app.post("/register/")
async def register_customer(request: Request):
    """Handle customer registration"""
    form_data = await request.form()

    try:
        customer_schema = SCustomersAdd(
            name=form_data.get('name'),
            surname=form_data.get('surname'),
            status=form_data.get('status'),
            email=form_data.get('email'),
            phone=form_data.get('phone'),
            password=form_data.get('password')
        )
        await add_customer(customer_schema, new_session)

        return templates.TemplateResponse('registration.html', {
            "request": request,
            "success": "Registration successful!",
            "success_show": True
        })
    except Exception as e:
        return templates.TemplateResponse('registration.html', {
            "request": request,
            "error": f"Registration failed: {str(e)}",
            "error_show": True
        })

@app.get("/login/")
async def login_page(request: Request):
    """Display customer login form"""
    return templates.TemplateResponse('login.html', {
        "request": request
    })

@app.post("/login/")
async def login_customer(request: Request):
    """Handle customer login"""
    form_data = await request.form()
    email = form_data.get('email')
    password = form_data.get('password')

    try:
        customer = await get_customer_by_email_password(email, password, new_session)
        
        if customer:
            # Set cookie with customer info
            response = RedirectResponse(url="/customer-profile/", status_code=303)
            response.set_cookie(key="customer_id", value=str(customer['id']), httponly=True)
            response.set_cookie(key="customer_name", value=customer['name'], httponly=False)
            response.set_cookie(key="customer_email", value=customer['email'], httponly=False)
            return response
        else:
            return templates.TemplateResponse('login.html', {
                "request": request,
                "error": "Invalid email or password",
                "error_show": True
            })
    except Exception as e:
        return templates.TemplateResponse('login.html', {
            "request": request,
            "error": f"Login failed: {str(e)}",
            "error_show": True
        })

@app.get("/customer-profile/")
async def customer_profile(request: Request):
    """Display customer profile with available tours"""
    customer_id = request.cookies.get('customer_id')
    customer_name = request.cookies.get('customer_name')
    customer_email = request.cookies.get('customer_email')

    if not customer_id:
        return RedirectResponse(url="/login/", status_code=303)

    tours_list = await get_tours_detailed(new_session)

    return templates.TemplateResponse('customer_profile.html', {
        "request": request,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "customer_email": customer_email,
        "tours": tours_list
    })

@app.get("/logout/")
async def logout():
    """Logout customer and clear cookies"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="customer_id")
    response.delete_cookie(key="customer_name")
    response.delete_cookie(key="customer_email")
    return response

@app.get("/customer/")
async def customer_page(request: Request):
    """Customer dashboard to choose and edit tours"""
    selected_id = request.query_params.get('tour_id')
    selected_tour_id = int(selected_id) if selected_id else None
    selected_customer_id = request.query_params.get('customer_id')

    selected_customer=await get_customer_by_id(selected_customer_id,new_session) if selected_customer_id else None

    tours_list = await get_tours_detailed(new_session)
    if not selected_tour_id and tours_list:
        selected_tour_id = tours_list[0]['id']

    selected_tour = None
    if selected_tour_id:
        selected_tour = await get_tour_by_id(selected_tour_id, new_session)

    hotels_list = await get_hotels(new_session)
    transfers_list = await get_transfers(new_session)
    transportations_list = await get_transports(new_session)

    
   

    

    return templates.TemplateResponse('customer.html', {
        "request": request,
        "tours": tours_list,
        "selected_tour": selected_tour,
        "hotels": hotels_list,
        "transfers": transfers_list,
        "transportations": transportations_list,
        "selected_tour_id": selected_tour_id,
        "selected_customer":selected_customer
    })


@app.post("/customer/")
async def customer_update(request: Request):
    """Allow customers to pick options and create orders. If tour params are modified, create a new tour; otherwise use existing."""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    selected_tour_id = to_int(form_data.get('selected_tour_id'))
    hotels_id = to_int(form_data.get('hotels_id'))
    transfer_id = to_int(form_data.get('transfer_id'))
    transport_id = to_int(form_data.get('transport_id'))
    selected_customer_id = to_int(form_data.get('customer_id'))
    selected_customer=await get_customer_by_id(selected_customer_id,new_session) if selected_customer_id else None
    is_modified = form_data.get('is_modified', 'false').lower() == 'true'

    # Basic validation: a tour and customer must be selected
    if not selected_tour_id or not selected_customer_id:
        tours_list = await get_tours_detailed(new_session)
        hotels_list = await get_hotels(new_session)
        transfers_list = await get_transfers(new_session)
        transportations_list = await get_transports(new_session)
        customers_list = await get_customers(new_session)

        

     

        return templates.TemplateResponse('customer.html', {
            "request": request,
            "tours": tours_list,
            "selected_tour": None,
            "hotels": hotels_list,
            "transfers": transfers_list,
            "transportations": transportations_list,
            
            "selected_tour_id": None,
            "selected_customer": selected_customer,
            "error": "Please choose a tour and customer before creating an order.",
            "error_show": True
        })

    async with new_session() as session:
        try:
            error_message = None
            tour_to_use_id = selected_tour_id
            
            # Load the existing tour to check if parameters changed
            tour_query = await session.execute(select(Tours).where(Tours.id == selected_tour_id))
            tour_obj = tour_query.scalar_one_or_none()

            if not tour_obj:
                raise ValueError("Selected tour not found")

            # Check if any parameters changed from the original tour
            params_changed = (
                hotels_id != tour_obj.hotels_id or
                transfer_id != tour_obj.transfer_id or
                transport_id != tour_obj.transport_id
            )

            # If parameters changed, create a new tour; otherwise use the existing one
            if is_modified or params_changed:
                tour_schema = SToursAdd(
                    name=tour_obj.name,
                    description=tour_obj.description,
                    transfer_id=transfer_id,
                    hotels_id=hotels_id,
                    transport_id=transport_id,
                )
                new_tour = await add_tour(tour_schema, session)
                tour_to_use_id = new_tour.id
            # else: keep tour_to_use_id = selected_tour_id (use existing tour)

            # Create order with the tour ID (either new or existing)
            order = SOrdersAdd(
                order_date=datetime.now().isoformat(timespec="seconds"),
                customer_id=selected_customer_id,
                tour_id=tour_to_use_id
            )

            await add_order(order, session)
            await session.commit()

            success_message = f"Order created successfully with {'new' if params_changed else 'existing'} tour!"
        except Exception as e:
            await session.rollback()
            success_message = None
            error_message = f"Error creating order: {str(e)}"

    # Refresh data for the page using a new session factory
    tours_list = await get_tours_detailed(new_session)
    selected_tour = await get_tour_by_id(selected_tour_id, new_session)
    hotels_list = await get_hotels(new_session)
    transfers_list = await get_transfers(new_session)
    transportations_list = await get_transports(new_session)
    customers_list = await get_customers(new_session)

    
    

    return templates.TemplateResponse('customer.html', {
        "request": request,
        "tours": tours_list,
        "selected_tour": selected_tour,
        "hotels": hotels_list,
        "transfers": transfers_list,
        "transportations": transportations_list,
        "selected_tour_id": selected_tour_id,
        "selected_customer": selected_customer,
        "success": success_message,
        "success_show": bool(success_message),
        "error": None if success_message else error_message,
        "error_show": not bool(success_message)
    })


if __name__ == "__main__":
    
    uvicorn.run("main:app", reload=True)