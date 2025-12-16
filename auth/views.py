from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from crud import add_customer, get_customer_by_email_password
from db_helper import db_helper
from database import Orders
from starlette.templating import Jinja2Templates
from schemas import SCustomersAdd, SOrders, SOrdersAdd, STours

router = APIRouter(tags=["Auth"])
templates = Jinja2Templates(directory="templates")

@router.get("/login/")
async def login_page(request: Request):
    """Display customer login form"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/")
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
    
@router.get("/logout/")
async def logout():
    """Logout customer and clear cookies"""
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="customer_id")
    response.delete_cookie(key="customer_name")
    response.delete_cookie(key="customer_email")
    return response

@router.get("/register/")
async def register_page(request: Request):
    """Display customer registration form"""
    return templates.TemplateResponse("registration.html", {"request": request})


@router.post("/register/")
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


