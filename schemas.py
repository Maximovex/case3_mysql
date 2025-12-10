from pydantic import BaseModel, EmailStr



class SToursAdd(BaseModel):
    name: str
    description: str | None = None
    transfer_id: int | None = None
    hotels_id: int | None = None
    transport_id: int | None = None

class STours(SToursAdd):
    id: int


class STransportAdd(BaseModel):
    type: str
    company: str
    price: int | None = None
    from_location: str | None = None
    to_location: str | None = None
    from_date: str | None = None
    to_date: str | None = None

class STransport(STransportAdd):
    id: int


class STransferAdd(BaseModel):
    type: str
    price: int | None = None

class STransfer(STransferAdd):
    id: int


class SHotelsAdd(BaseModel):
    name: str
    location: str
    rating: int | None = None
    price: int | None = None
    description: str | None = None

class SHotels(SHotelsAdd):
    id: int



class SCustomersAdd(BaseModel):
    
    name: str
    surname: str
    status: str
    email: EmailStr
    phone: str
    password:str
    

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