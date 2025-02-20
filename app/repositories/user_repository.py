from app.config.database import database
from app.models.user import UserModel
from bson import ObjectId
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.models.common import PaginationParams

class UserRepository(BaseRepository):
    collection = database.users

    async def create(self, user: UserModel):
        user_dict = user.dict()
        result = await self.collection.insert_one(user_dict)
        return str(result.inserted_id)

    async def get_all(self, pagination: PaginationParams = None, filters: dict = None):
        if pagination is None:
            pagination = PaginationParams()
        
        return await self.paginate_and_filter(self.collection, pagination, filters)

    async def get_by_id(self, id: str):
        user = await self.collection.find_one({"_id": ObjectId(id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def get_by_email(self, email: str):
        user = await self.collection.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def update(self, id: str, data: dict):
        data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        return await self.get_by_id(id)
        
    async def delete(self, id: str):
        await self.collection.delete_one({"_id": ObjectId(id)})
        return True

    async def add_purchased_product(self, user_id: str, product_id: str):
        """Add a product to user's purchased products list"""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"purchased_products": ObjectId(product_id)}}
        )

    async def remove_purchased_product(self, user_id: str, product_id: str):
        """Remove a product from user's purchased products list"""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$pull": {"purchased_products": ObjectId(product_id)}}
        )

    async def get_purchased_products(self, user_id: str, pagination: PaginationParams):
        """Get all products purchased by user with pagination"""
        user = await self.get_by_id(user_id)
        if not user or "purchased_products" not in user:
            return {"total": 0, "items": []}

        skip = (pagination.page - 1) * pagination.limit
        
        pipeline = [
            {"$match": {"_id": ObjectId(user_id)}},
            {"$unwind": "$purchased_products"},
            {"$lookup": {
                "from": "products",
                "localField": "purchased_products",
                "foreignField": "_id",
                "as": "product"
            }},
            {"$unwind": "$product"},
            {"$facet": {
                "total": [{"$count": "count"}],
                "items": [
                    {"$skip": skip},
                    {"$limit": pagination.limit},
                    {"$replaceRoot": {"newRoot": "$product"}},
                    {"$addFields": {
                        "_id": {"$toString": "$_id"}
                    }}
                ]
            }}
        ]

        if pagination.sort_by:
            sort_order = 1 if pagination.sort_order == "asc" else -1
            pipeline[4]["$facet"]["items"].insert(
                0, {"$sort": {f"product.{pagination.sort_by}": sort_order}}
            )

        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if not result:
            return {"total": 0, "items": []}
            
        result = result[0]
        total = result["total"][0]["count"] if result["total"] else 0
        
        # Convert any remaining ObjectIds to strings in the items
        items = result["items"]
        for item in items:
            if "supplier_id" in item and isinstance(item["supplier_id"], ObjectId):
                item["supplier_id"] = str(item["supplier_id"])
        
        return {
            "total": total,
            "items": items
        }