from fastapi import FastAPI,Depends
from schemas import SToursAdd, STours
from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,async_sessionmaker,session


app = FastAPI()

@app.get("/tours/")
def read_tours():
    tours = session.query(Tours).all()
    return tours

@app.post("/tours/")
async def create_tour(data: SToursAdd=Depends()):
    tour_dict=data.model_dump()
    tour = Tours(**tour_dict)
    session.add(tour)
    await session.flush()
    await session.commit()
    return tour