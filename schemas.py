from pydantic import BaseModel

class SToursAdd(BaseModel):
    name: str
    customer_id: int | None = None
    transfer_id: int | None = None
    hotels_id: int | None = None
    transport_id: int | None = None
    total_cost: int | None = None

class STours(SToursAdd):
    id: int