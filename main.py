from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi.responses import Response
from database import (
    Tours,
    Customers,
    Orders,
    Managers,
    Hotels,
    Transportations,
    Transfers,
)
from sqlalchemy import select
from crud import (
    get_customer_by_id,
    add_transport,
    add_transfer,
    get_transfers,
    get_transports,
    add_customer,
    get_customers,
    add_order,
    get_customer_by_email_password,
)
from tour.crud import (
    add_tour,
    get_tour_by_id,
    get_tours_detailed,
    update_tour,
    delete_tour,
)

from hotel.crud import get_hotels

from schemas import (
    SToursAdd,
    STransportAdd,
    STransferAdd,
    SHotelsAdd,
    SCustomersAdd,
    SOrdersAdd,
)
import uvicorn
from datetime import datetime
from tour.views import router as tour_router
from hotel.views import router as hotel_router
from order.views import router as order_router
from auth import router as auth_router
from db_helper import db_helper

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.include_router(tour_router, prefix="/tour")
app.include_router(hotel_router, prefix="/hotel")
app.include_router(order_router, prefix="/order")
app.include_router(auth_router,prefix="/auth")

@app.get("/")
async def tours_page(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    result = await get_tours_detailed(session)

    return templates.TemplateResponse(        "tours.html", {"request": request, "tours": result})





@app.get("/customers/")
async def read_customers(session: AsyncSession = Depends(db_helper.session_dependency)):
    customers = await session.execute(select(Customers))
    return customers.scalars().all()


@app.get("/managers/")
async def read_managers(session: AsyncSession = Depends(db_helper.session_dependency)):
    managers = await session.execute(select(Managers))
    return managers.scalars().all()


@app.get("/register/")
async def register_page(request: Request):
    """Display customer registration form"""
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/register/")
async def register_customer(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Handle customer registration"""
    form_data = await request.form()

    try:
        customer_schema = SCustomersAdd(
            name=form_data.get("name"),
            surname=form_data.get("surname"),
            status=form_data.get("status"),
            email=form_data.get("email"),
            phone=form_data.get("phone"),
            password=form_data.get("password"),
        )
        await add_customer(customer_schema, session)

        return templates.TemplateResponse(
            "registration.html",
            {
                "request": request,
                "success": "Registration successful!",
                "success_show": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "registration.html",
            {
                "request": request,
                "error": f"Registration failed: {str(e)}",
                "error_show": True,
            },
        )


@app.get("/login/")
async def login_page(request: Request):
    """Display customer login form"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login/")
async def login_customer(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Handle customer login"""
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")

    try:
        customer = await get_customer_by_email_password(email, password, session)

        if customer:
            # Set cookie with customer info
            response = RedirectResponse(url="/customer-profile/", status_code=303)
            response.set_cookie(
                key="customer_id", value=str(customer["id"]), httponly=True
            )
            response.set_cookie(
                key="customer_name", value=customer["name"], httponly=False
            )
            response.set_cookie(
                key="customer_email", value=customer["email"], httponly=False
            )
            return response
        else:
            return templates.TemplateResponse(
                "login.html",
                {
                    "request": request,
                    "error": "Invalid email or password",
                    "error_show": True,
                },
            )
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": f"Login failed: {str(e)}",
                "error_show": True,
            },
        )


@app.get("/customer-profile/")
async def customer_profile(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Display customer profile with available tours"""
    customer_id = request.cookies.get("customer_id")
    customer_name = request.cookies.get("customer_name")
    customer_email = request.cookies.get("customer_email")

    if not customer_id:
        return RedirectResponse(url="/login/", status_code=303)

    tours_list = await get_tours_detailed(session)

    return templates.TemplateResponse(
        "customer_profile.html",
        {
            "request": request,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "tours": tours_list,
        },
    )


@app.get("/logout/")
async def logout():
    """Logout customer and clear cookies"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="customer_id")
    response.delete_cookie(key="customer_name")
    response.delete_cookie(key="customer_email")
    return response


@app.get("/customer/")
async def customer_page(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Customer dashboard to choose and edit tours"""
    selected_id = request.query_params.get("tour_id")
    selected_tour_id = int(selected_id) if selected_id else None
    selected_customer_id = request.query_params.get("customer_id")

    selected_customer = (
        await get_customer_by_id(selected_customer_id, session)
        if selected_customer_id
        else None
    )

    tours_list = await get_tours_detailed(session)
    if not selected_tour_id and tours_list:
        selected_tour_id = tours_list[0]["id"]

    selected_tour = None
    if selected_tour_id:
        selected_tour = await get_tour_by_id(selected_tour_id, session)

    hotels_list = await get_hotels(session)
    transfers_list = await get_transfers(session)
    transportations_list = await get_transports(session)
    return templates.TemplateResponse(
        "customer.html",
        {
            "request": request,
            "tours": tours_list,
            "selected_tour": selected_tour,
            "hotels": hotels_list,
            "transfers": transfers_list,
            "transportations": transportations_list,
            "selected_tour_id": selected_tour_id,
            "selected_customer": selected_customer,
        },
    )


@app.post("/customer/")
async def customer_update(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Allow customers to pick options and create orders. If tour params are modified, create a new tour; otherwise use existing."""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    selected_tour_id = to_int(form_data.get("selected_tour_id"))
    hotels_id = to_int(form_data.get("hotels_id"))
    transfer_id = to_int(form_data.get("transfer_id"))
    transport_id = to_int(form_data.get("transport_id"))
    selected_customer_id = to_int(form_data.get("customer_id"))
    selected_customer = (
        await get_customer_by_id(selected_customer_id, session)
        if selected_customer_id
        else None
    )
    is_modified = form_data.get("is_modified", "false").lower() == "true"

    # Basic validation: a tour and customer must be selected
    if not selected_tour_id or not selected_customer_id:
        tours_list = await get_tours_detailed(session)
        hotels_list = await get_hotels(session)
        transfers_list = await get_transfers(session)
        transportations_list = await get_transports(session)
        customers_list = await get_customers(session)
        return templates.TemplateResponse(
            "customer.html",
            {
                "request": request,
                "tours": tours_list,
                "selected_tour": None,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "selected_tour_id": None,
                "selected_customer": selected_customer,
                "error": "Please choose a tour and customer before creating an order.",
                "error_show": True,
            },
        )

    try:
        error_message = None
        tour_to_use_id = selected_tour_id

        # Load the existing tour to check if parameters changed
        tour_query = await session.execute(
            select(Tours).where(Tours.id == selected_tour_id)
        )
        tour_obj = tour_query.scalar_one_or_none()

        if not tour_obj:
            raise ValueError("Selected tour not found")

        # Check if any parameters changed from the original tour
        params_changed = (
            hotels_id != tour_obj.hotels_id
            or transfer_id != tour_obj.transfer_id
            or transport_id != tour_obj.transport_id
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
            tour_id=tour_to_use_id,
        )

        await add_order(order, session)
        await session.commit()

        success_message = f"Order created successfully with {'new' if params_changed else 'existing'} tour!"
    except Exception as e:
        await session.rollback()
        success_message = None
        error_message = f"Error creating order: {str(e)}"

    # Refresh data for the page using a new session factory
    tours_list = await get_tours_detailed(session)
    selected_tour = await get_tour_by_id(selected_tour_id, session)
    hotels_list = await get_hotels(session)
    transfers_list = await get_transfers(session)
    transportations_list = await get_transports(session)
    customers_list = await get_customers(session)
    return templates.TemplateResponse(
        "customer.html",
        {
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
            "error_show": not bool(success_message),
        },
    )


if __name__ == "__main__":

    uvicorn.run("main:app", reload=True)
