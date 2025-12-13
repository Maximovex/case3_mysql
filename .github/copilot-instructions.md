# World Travel - FastAPI Tour Management System

## Architecture Overview

This is a FastAPI application for managing tours, hotels, transportations, and customer bookings with async MySQL via SQLAlchemy. The app uses server-side rendered templates (Jinja2) with cookie-based authentication.

**Core Components:**
- `main.py` - FastAPI app setup, root routes, and authentication (login/register)
- `database.py` - SQLAlchemy ORM models (Tours, Hotels, Transportations, Transfers, Customers, Orders, Managers)
- `schemas.py` - Pydantic models for request/response validation
- `db_helper.py` - Database session management with scoped async sessions
- Feature modules: `tour/`, `hotel/`, `order/` (each with `crud.py` and `views.py`)

## Database Connection

**MySQL + aiomysql:** Connection string in `settings.py`:
```python
MY_DATABASE_URL="mysql+aiomysql://root:f6d8lini@localhost:3306/world_travel"
```

**Session Management:** Use `db_helper.session_dependency` in route dependencies:
```python
async def my_route(session: AsyncSession = Depends(db_helper.session_dependency)):
```

**Scoped Sessions:** `DBHelper.get_scoped_session()` creates task-scoped sessions that auto-cleanup via `session.remove()`.

## Module Structure Pattern

Each feature (tour, hotel, order) follows this structure:
- `crud.py` - Database operations (add, get, update, delete)
- `views.py` - FastAPI router with routes returning Jinja2 templates
- Routes mounted in `main.py` with prefixes: `/tour`, `/hotel`, `/order`

**Example:**
```python
# tour/views.py
router = APIRouter(tags=["tour"])

# main.py
app.include_router(tour_router, prefix="/tour")
```

## Key Patterns

### 1. CRUD Functions
All CRUD operations in `crud.py` files:
- Accept session via `Depends(db_helper.session_dependency)`
- Use `await session.flush()` to get IDs without committing
- Return ORM models, not Pydantic schemas
- **Commit in views, not CRUD** - allows rollback on errors

```python
# tour/crud.py
async def add_tour(tour: SToursAdd, session: AsyncSession):
    new_tour = Tours(**tour.model_dump())
    session.add(new_tour)
    await session.flush()  # Gets ID, doesn't commit
    return new_tour
```

### 2. Template Rendering with Forms
Routes handle both GET (display form) and POST (process form):
```python
@router.get("/add/")
async def add_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post("/add/")
async def create(request: Request, session: AsyncSession = Depends(...)):
    form_data = await request.form()
    # Process, commit, show success/error
    await session.commit()
    return templates.TemplateResponse("form.html", {"request": request, "success": "..."})
```

### 3. Detailed Tours with Relationships
`get_tours_detailed()` manually fetches related entities (hotel, transfer, transport) and calculates `total_cost`:
```python
tour_schema = STours.model_validate(tour)
if tour.hotels_id:
    hotel = await session.execute(select(Hotels).where(Hotels.id == tour.hotels_id))
    tour_schema.hotel = SHotels.model_validate(hotel.scalar_one_or_none())
```

**Why no ORM relationships?** Tours model has FKs but no explicit `relationship()` mappings - relationships loaded manually in CRUD.

### 4. Form Data Parsing
Convert form strings to integers with helper:
```python
def to_int(val):
    return int(val) if val not in (None, "") else None

rating = to_int(form_data.get("rating"))
```

### 5. Dependencies for Reusable Queries
`dependencies.py` provides common data fetching for dropdowns:
```python
async def get_hotels_dependency(session: AsyncSession = Depends(...)) -> list[Hotels]:
    return await get_hotels(session)
```

Use in routes needing hotel list for forms.

### 6. Cookie-Based Auth
Login sets cookies (`customer_id`, `customer_name`, `customer_email`):
```python
response = RedirectResponse(url="/customer-profile/", status_code=303)
response.set_cookie(key="customer_id", value=str(customer.id), httponly=True)
```

Protected routes check cookies:
```python
customer_id = request.cookies.get("customer_id")
if not customer_id:
    return RedirectResponse(url="/login/")
```

## Common Operations

**Run Server:**
```bash
uvicorn main:app --reload
```

**Database Schema:** MySQL Workbench file `world_travel.mwb` defines schema.

**Error Handling:** Views catch exceptions and render templates with `error` context variable for display.

## Conventions

- **Async everywhere** - all routes and CRUD functions are async
- **Template variables** - use `success` and `error` keys with `success_show`/`error_show` booleans for conditional display
- **ORM to Pydantic** - use `Model.model_validate(orm_instance)` or `model_dump()` for conversions
- **No autocommit** - explicit `await session.commit()` in views after successful operations
- **Flush for IDs** - use `flush()` when needing generated IDs before commit (e.g., creating related entities)

## Code Organization

- **Base CRUD** - `crud.py` (root) has customer, transport, transfer operations
- **Domain CRUD** - `tour/crud.py`, `hotel/crud.py`, `order/crud.py` for specific entities
- **Templates** - all Jinja2 templates in root `templates/` directory
- **Settings** - plaintext credentials in `settings.py` (not production-ready)
