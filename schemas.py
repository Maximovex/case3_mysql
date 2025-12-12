from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class SToursAdd(BaseModel):
    name: str
    description: str | None = None
    transfer_id: int | None = None
    hotels_id: int | None = None
    transport_id: int | None = None


class STours(SToursAdd):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hotel: SHotels | None = None
    transfer: STransfer | None = None
    transport: STransport | None = None
    total_cost: int | None = None


class STransportAdd(BaseModel):
    type: str | None = None
    company: str | None = None
    price: int | None = None
    from_location: str | None = None
    to_location: str | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


class STransport(STransportAdd):
    model_config = ConfigDict(from_attributes=True)
    id: int


class STransferAdd(BaseModel):
    type: str
    price: int | None = None


class STransfer(STransferAdd):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SHotelsAdd(BaseModel):
    name: str
    location: str
    rating: int | None = None
    price: int | None = None
    description: str | None = None


class SHotels(SHotelsAdd):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SCustomersAdd(BaseModel):

    name: str
    surname: str
    status: str
    email: EmailStr
    phone: str
    password: str


class SCustomers(SCustomersAdd):
    id: int


class SOrdersAdd(BaseModel):
    order_date: str
    customer_id: int | None = None
    tour_id: int | None = None
    total_amount: int | None = None
    payment_status: int | None = None
    manager_id: int | None = None


class SOrders(SOrdersAdd):
    id: int


class SManagersAdd(BaseModel):
    name: str
    surname: str
    email: EmailStr
    phone: str


class SManagers(SManagersAdd):
    id: int
