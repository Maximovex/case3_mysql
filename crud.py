from database import Base, Tours, Customers, Orders, Managers, Hotels, Transportations,session,AsyncSession

class TourCRUD:
    def __init__(self, db_session:AsyncSession):
        self.db_session = db_session

    async def create_tour(self,name, customer_id=None, transfer_id=None, hotels_id=None, transport_id=None, total_cost=None)-> Tours:
        
        new_tour = Tours(
            name=name,
            customer_id=customer_id,
            transfer_id=transfer_id,
            hotels_id=hotels_id,
            transport_id=transport_id,
            total_cost=total_cost
        )
        self.db_session.add(new_tour)
        await self.db_session.flush()
        return new_tour