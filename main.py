from fastapi import FastAPI,Depends
from pydantic import BaseModel
from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,session

class SToursAdd(BaseModel):
    name: str
    customer_id: int
    transfer_id: int
    hotels_id: int
    transport_id: int
    total_cost: int

class STours(SToursAdd):
    id: int

app = FastAPI()

@app.get("/tours/")
def read_tours():
    tours = session.query(Tours).all()
    return tours

@app.post("/tours/")
async def create_tour(tour: SToursAdd=Depends()):
    
    session.add(tour)
    session.commit()
    return tour