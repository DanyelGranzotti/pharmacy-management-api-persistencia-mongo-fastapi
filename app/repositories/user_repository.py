from app.config.database import database
from app.models.user import UserModel
from bson import ObjectId
from datetime import datetime
from app.repositories.base_repository import BaseRepository
from app.models.common import PaginationParams
from app.utils.mongo_utils import convert_mongo_document

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
        return convert_mongo_document(user)

    async def get_by_email(self, email: str):
        user = await self.collection.find_one({"email": email})
        return convert_mongo_document(user)

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
                    {"$replaceRoot": {"newRoot": "$product"}}
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
        
        # Convert ObjectIds in items
        items = [convert_mongo_document(item) for item in result["items"]]
        
        return {
            "total": total,
            "items": items
        }

    async def update_bank_balance(self, user_id: str, new_balance: float):
        """Update user's bank account balance"""
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "bank_account.balance": new_balance,
                "updated_at": datetime.utcnow()
            }}
        )
        return await self.get_by_id(user_id)

    async def get_bank_account(self, user_id: str):
        """Get user's bank account information"""
        user = await self.get_by_id(user_id)
        return user.get("bank_account") if user else None

    async def deposit(self, user_id: str, amount: float):
        """Make a deposit to user's bank account"""
        user = await self.get_by_id(user_id)
        if not user or "bank_account" not in user:
            return None
            
        current_balance = user["bank_account"]["balance"]
        new_balance = current_balance + amount
        
        await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "bank_account.balance": new_balance,
                "updated_at": datetime.utcnow()
            }}
        )
        return await self.get_by_id(user_id)