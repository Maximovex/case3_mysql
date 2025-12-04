from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,session

class ObjectCRUD:
    @classmethod
    async def create(cls):
        async with session() as s:
            new_tour = Tours(
                name=tour.name,
                customer_id=tour.customer_id,
                transfer_id=tour.transfer_id,
                hotels_id=tour.hotels_id,
                transport_id=tour.transport_id,
                total_cost=tour.total_cost
            )
            s.add(new_tour)
            await s.commit()
            await s.refresh(new_tour)
            return new_tour.id 