
from sqlalchemy.ext.asyncio import async_sessionmaker,create_async_engine,AsyncSession
from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import DeclarativeBase,relationship
from datetime import datetime
from settings import MY_DATABASE_URL


engine = create_async_engine(MY_DATABASE_URL, echo=True)
new_session=async_sessionmaker(engine,expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class Tours(Base):
    __tablename__ = 'tours'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255),nullable=False)
    description=Column(String(1000),nullable=True)
    transfer_id=Column(Integer,ForeignKey('transfer.id'),nullable=True)
    hotels_id=Column(Integer,ForeignKey('hotels.id'),nullable=True)
    transport_id=Column(Integer,ForeignKey('transportations.id'),nullable=True)
    total_cost=Column(Integer,nullable=True)

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, description={self.description}, transfer_id={self.transfer_id}, hotels_id={self.hotels_id}, transport_id={self.transport_id}, total_cost={self.total_cost})"

class Customers(Base):
    __tablename__ = 'customers'
    id=Column(Integer, primary_key=True,index=True)
    name=Column(String(255))
    surname=Column(String(255))
    status=Column(String(50))
    email=Column(String(255))
    phone=Column(String(20))
    order_id=Column(Integer,ForeignKey('orders.id'))

    def __repr__(self):
        return f"(id={self.id}, name={self.name}, surname={self.surname}, status={self.status}, email={self.email}, phone={self.phone}, order_id={self.order_id})"

class Orders(Base):
    __tablename__ = 'orders'
    id=Column(Integer, primary_key=True,index=True)
    order_date=Column(String(50))
    customer_id=Column(Integer,ForeignKey('customers.id'))
    tour_id=Column(Integer,ForeignKey('tours.id'))
    total_amount=Column(Integer)
    payment_status=Column(Integer)
    manager_id=Column(Integer,ForeignKey('managers.id'))

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
    description=Column(String(1000),nullable=True)

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
