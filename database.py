
from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine,AsyncSession
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


engine = create_async_engine('mysql+aiomysql://root:f6d8lini@localhost:3306/world_travel', echo=True)
AsyncSession=async_sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)
session=AsyncSession()

class Base(DeclarativeBase):
    pass

class Tours(Base):
    __tablename__ = 'tours'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255))
    customer_id=Column(Integer)
    transfer_id=Column(Integer)
    hotels_id=Column(Integer)
    transport_id=Column(Integer)
    total_cost=Column(Integer)

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, customer_id={self.customer_id}, transfer_id={self.transfer_id}, hotels_id={self.hotels_id}, transport_id={self.transport_id}, total_cost={self.total_cost})"

class Customers(Base):
    __tablename__ = 'customers'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255))
    surname=Column(String(255))
    status=Column(String(50))
    email=Column(String(255))
    phone=Column(String(20))
    order_id=Column(Integer)

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, surname={self.surname}, status={self.status}, email={self.email}, phone={self.phone}, order_id={self.order_id})"

class Orders(Base):
    __tablename__ = 'orders'
    id=Column(Integer, primary_key=True,index=True)
    order_date=Column(String(50))
    customer_id=Column(Integer)
    tour_id=Column(Integer)
    total_amount=Column(Integer)
    payment_status=Column(Integer)
    manager_id=Column(Integer)

    def __repr__(self):
        return f"(id={self.id}, order_date={self.order_date}, customer_id={self.customer_id}, tour_id={self.tour_id}, total_amount={self.total_amount}, payment_status={self.payment_status}, manager_id={self.manager_id})"

class Managers(Base):
    __tablename__ = 'managers'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255))
    surname=Column(String(255))
    email=Column(String(255))
    phone=Column(String(20))

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, surname={self.surname}, email={self.email}, phone={self.phone})"

class Hotels(Base):
    __tablename__ = 'hotels'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255))
    location=Column(String(255))
    rating=Column(Integer)
    price=Column(Integer)

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, location={self.location}, rating={self.rating}, price={self.price})"
    
class Transportations(Base):
    __tablename__ = 'transportations'
    id=Column(Integer, primary_key=True,index=True)
    type=Column(String(50))
    company=Column(String(255))
    price=Column(Integer)
    from_location=Column(String(255))
    to_location=Column(String(255))
    from_date=Column(String(50))
    to_date=Column(String(50))

    def __repr__(self):
        return f"(id={self.id}, type={self.type}, company={self.company}, price={self.price})"
