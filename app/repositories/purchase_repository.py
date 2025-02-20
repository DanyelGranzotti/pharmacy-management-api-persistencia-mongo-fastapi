from app.config.database import database
from app.models.purchase import PurchaseModel
from bson import ObjectId
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.models.common import PaginationParams

class PurchaseRepository(BaseRepository):
    collection = database.purchases

    async def create(self, purchase: PurchaseModel):
        purchase_dict = purchase.dict()
        purchase_dict["updated_at"] = datetime.utcnow()
        result = await self.collection.insert_one(purchase_dict)
        return str(result.inserted_id)

    async def get_all(self, pagination: PaginationParams = None, filters: dict = None):
        if pagination is None:
            pagination = PaginationParams()
        
        return await self.paginate_and_filter(self.collection, pagination, filters)

    async def get_by_id(self, id: str):
        purchase = await self.collection.find_one({"_id": ObjectId(id)})
        if purchase:
            purchase["_id"] = str(purchase["_id"])
        return purchase

    async def get_by_user(self, user_id: str, pagination: PaginationParams = None):
        if pagination is None:
            pagination = PaginationParams()
        
        filters = {"user_id": user_id}
        return await self.paginate_and_filter(self.collection, pagination, filters)

    async def update(self, id: str, data: dict):
        data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        return await self.get_by_id(id)
    
    async def delete(self, id: str):
        await self.collection.delete_one({"_id": ObjectId(id)})
        return True
