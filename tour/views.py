from fastapi import APIRouter, Depends, Request, Form
from fastapi.templating import Jinja2Templates
from crud import add_transfer, add_transport, get_transfers, get_transports
from db_helper import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

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
from hotel.crud import get_hotels
from tour.crud import (
    get_tours_detailed,
    add_tour,
    get_tour_by_id,
    update_tour,
    delete_tour,
)
from dependencies import (
    get_hotels_dependency,
    get_transfers_dependency,
    get_transports_dependency,
)
from schemas import (
    SToursAdd,
    STours,
    STransportAdd,
    STransferAdd,
    SHotelsAdd,
    SCustomersAdd,
    SOrdersAdd,
)

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["tour"])


@router.get("/")
async def get_tour_page(
    request: Request,
    hotels_list: list[Hotels] = Depends(get_hotels_dependency),
    transfers_list: list[Transfers] = Depends(get_transfers_dependency),
    transportations_list: list[Transportations] = Depends(get_transports_dependency),
):
    """Display the add tour form with available hotels, transfers, and transportations"""

    return templates.TemplateResponse(
        "addtour.html",
        {
            "request": request,
            "hotels": hotels_list,
            "transfers": transfers_list,
            "transportations": transportations_list,
        },
    )


@router.post("/")
async def create_tour(
    request: Request, transport_schema:Annotated[STransportAdd,Form()],     session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Handle form submission to create a new tour. Allows creating transfer/transportation on the fly."""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    # Existing selections (ids) if chosen
    transfer_id = to_int(form_data.get("transfer_id"))
    transport_id = to_int(form_data.get("transport_id"))
    hotels_id = to_int(form_data.get("hotels_id"))

    # New transfer fields
    transfer_schema = None
    if form_data.get("new_transfer_type"):
        transfer_schema = STransferAdd(
            type=form_data.get("new_transfer_type"),
            price=to_int(form_data.get("new_transfer_price")),
        )

    
    try:
        # Create transfer if no id provided but new data given
        if not transfer_id and transfer_schema:
            created_transfer = await add_transfer(transfer_schema, session)
            transfer_id = created_transfer.id

        # Create transportation if no id provided but new data given
        if not transport_id and transport_schema:
            created_transport = await add_transport(transport_schema, session)
            transport_id = created_transport.id

        # Create tour using schema
        tour_schema = SToursAdd(
            name=form_data.get("name"),
            description=form_data.get("description"),
            transfer_id=transfer_id,
            hotels_id=hotels_id,
            transport_id=transport_id,
        )
        await add_tour(tour_schema, session)
        await session.commit()

        # Fetch fresh data for response
        hotels_list = await get_hotels(session)
        transfers_list = await get_transfers(session)
        transportations_list = await get_transports(session)

        return templates.TemplateResponse(
            "addtour.html",
            {
                "request": request,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "success": "Tour created successfully! 🎉",
                "success_show": True,
            },
        )
    except Exception as e:
        await session.rollback()

        # Fetch fresh data for error response
        hotels_list = await get_hotels(session)
        transfers_list = await get_transfers(session)
        transportations_list = await get_transports(session)

        return templates.TemplateResponse(
            "addtour.html",
            {
                "request": request,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "error": f"Error creating tour: {str(e)}",
                "error_show": True,
            },
        )


@router.get("/update/")
async def update_tours_page(
    request: Request, session: AsyncSession = Depends(db_helper.session_dependency)
):
    """Display list of tours for updating"""
    result = await get_tours_detailed(session)
    return templates.TemplateResponse(
        "update_tours.html", {"request": request, "tours": result}
    )


@router.get("/{tour_id}")
async def tour_page(
    request: Request,
    tour_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Display tour details and update form"""
    tour = await get_tour_by_id(tour_id, session)

    if not tour:
        return templates.TemplateResponse(
            "tour.html", {"request": request, "tour": None}
        )

    hotels_list = await get_hotels(session)
    transfers_list = await get_transfers(session)
    transportations_list = await get_transports(session)

    # Convert ORM objects to dictionaries

    return templates.TemplateResponse(
        "tour.html",
        {
            "request": request,
            "tour": tour,
            "hotels": hotels_list,
            "transfers": transfers_list,
            "transportations": transportations_list,
        },
    )


@router.patch("/{tour_id}")
async def update_tour_handler(
    request: Request,
    tour_schema: Annotated[SToursAdd, Form()],
    tour_id: int,
    transport_schema: Annotated[STransportAdd, Form()],
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Handle tour update form submission"""
    form_data = await request.form()

    def to_int(val):
        return int(val) if val not in (None, "") else None

    # Get existing selection ids
    transfer_id = to_int(form_data.get("transfer_id"))
    transport_id = to_int(form_data.get("transport_id"))

    # New transfer fields
    transfer_schema = STransferAdd(
        type=form_data.get("new_transfer_type"),
        price=to_int(form_data.get("new_transfer_price")),
    )

    # New transportation fields

    try:
        # Create transfer if no id provided but new data given
        if not transfer_id and transfer_schema:

            created_transfer = await add_transfer(transfer_schema, session)
            transfer_id = created_transfer.id

        # Create transportation if no id provided but new data given
        if not transport_id and transport_schema:

            created_transport = await add_transport(transport_schema, session)
            transport_id = created_transport.id

        # Update tour using schema
        tour_schema.transfer_id = transfer_id
        tour_schema.transport_id = transport_id
        await update_tour(tour_id, tour_schema, session)
        await session.commit()

        # Fetch updated tour data
        tour = await get_tour_by_id(tour_id, session)
        hotels_list = await get_hotels(session)
        transfers_list = await get_transfers(session)
        transportations_list = await get_transports(session)

        return templates.TemplateResponse(
            "tour.html",
            {
                "request": request,
                "tour": tour,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "success": "Tour updated successfully! 🎉",
                "success_show": True,
            },
        )
    except Exception as e:
        await session.rollback()

        # Fetch tour data for error response
        tour = await get_tour_by_id(tour_id, session)
        hotels_list = await get_hotels(session)
        transfers_list = await get_transfers(session)
        transportations_list = await get_transports(session)

        return templates.TemplateResponse(
            "tour.html",
            {
                "request": request,
                "tour": tour,
                "hotels": hotels_list,
                "transfers": transfers_list,
                "transportations": transportations_list,
                "error": f"Error updating tour: {str(e)}",
                "error_show": True,
            },
        )


@router.delete("/{tour_id}/delete")
async def delete_tour_handler(
    request: Request,
    tour_id: int,
    session: AsyncSession = Depends(db_helper.session_dependency),
):
    """Handle tour deletion"""
    try:
        success = await delete_tour(tour_id, session)

        if success:
            # Redirect to update tours page after successful deletion
            from fastapi.responses import RedirectResponse

            return RedirectResponse(url="/update-tours/", status_code=303)
        else:
            # Tour not found
            result = await get_tours_detailed(session)
            return templates.TemplateResponse(
                "update_tours.html",
                {
                    "request": request,
                    "tours": result,
                    "error": "Tour not found",
                    "error_show": True,
                },
            )
    except Exception as e:
        # Error during deletion
        result = await get_tours_detailed(session)
        return templates.TemplateResponse(
            "update_tours.html",
            {
                "request": request,
                "tours": result,
                "error": f"Error deleting tour: {str(e)}",
                "error_show": True,
            },
        )
