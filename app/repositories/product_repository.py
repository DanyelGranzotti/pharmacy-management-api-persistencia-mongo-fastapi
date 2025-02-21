from typing import Dict, Any
from bson import ObjectId, errors
from fastapi import HTTPException
from app.models.product import ProductModel
from app.models.common import PaginationParams
from app.config.database import database
from app.utils.mongo_utils import convert_mongo_document
from datetime import datetime

class ProductRepository:
    collection = database.products

    async def create(self, product: ProductModel) -> str:
        try:
            # Validar se o ID do fornecedor é um ObjectId válido
            supplier_id = ObjectId(product.supplier_id)
        except errors.InvalidId:
            raise HTTPException(
                status_code=400,
                detail="Invalid supplier ID format"
            )

        # Verificar se o fornecedor existe
        supplier = await database.suppliers.find_one({"_id": supplier_id})
        if not supplier:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier with ID {product.supplier_id} not found"
            )
            
        result = await self.collection.insert_one(product.model_dump())
        return str(result.inserted_id)

    async def get_by_id(self, id: str) -> Dict[str, Any]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        return convert_mongo_document(document)

    async def get_all(self, pagination: PaginationParams, filters: Dict = None):
        skip = (pagination.page - 1) * pagination.limit
        
        query = {}
        if filters:
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, dict):  # For price range queries
                        query[key] = value
                    else:
                        query[key] = value

        cursor = self.collection.find(query)

        if pagination.sort_by:
            sort_order = 1 if pagination.sort_order == "asc" else -1
            cursor = cursor.sort(pagination.sort_by, sort_order)

        total = await self.collection.count_documents(query)
        products = await cursor.skip(skip).limit(pagination.limit).to_list(None)
        
        return {
            "total": total,
            "page": pagination.page,
            "limit": pagination.limit,
            "products": [convert_mongo_document(p) for p in products]
        }

    async def update(self, id: str, update_data: Dict) -> Dict[str, Any]:
        if "supplier_id" in update_data:
            supplier = await database.suppliers.find_one({"_id": ObjectId(update_data["supplier_id"])})
            if not supplier:
                raise HTTPException(status_code=404, detail="Supplier not found")
        
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return await self.get_by_id(id)

    async def delete(self, id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def get_products_with_supplier_details(self, pagination: PaginationParams, filters: Dict = None):
        """
        Get products with detailed supplier information and sales statistics
        """
        skip = (pagination.page - 1) * pagination.limit
        
        match_stage = {}
        if filters:
            match_stage.update(filters)

        pipeline = [
            {"$match": match_stage},
            {"$lookup": {
                "from": "suppliers",
                "localField": "supplier_id",
                "foreignField": "_id",
                "as": "supplier"
            }},
            {"$unwind": "$supplier"},
            {"$lookup": {
                "from": "purchases",
                "localField": "_id",
                "foreignField": "product_id",
                "as": "sales"
            }},
            {"$addFields": {
                "total_sales": {"$size": "$sales"},
                "total_quantity_sold": {"$sum": "$sales.quantity"}
            }},
            {"$facet": {
                "metadata": [{"$count": "total"}],
                "data": [
                    {"$sort": {pagination.sort_by: 1 if pagination.sort_order == "asc" else -1}}
                    if pagination.sort_by else {"$sort": {"name": 1}},
                    {"$skip": skip},
                    {"$limit": pagination.limit}
                ]
            }}
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)
        
        if not result or not result[0]["metadata"]:
            return {"total": 0, "products": []}

        return {
            "total": result[0]["metadata"][0]["total"],
            "products": [convert_mongo_document(p) for p in result[0]["data"]]
        }

    async def get_product_sales_analytics(self, start_date: datetime = None, end_date: datetime = None):
        """
        Get detailed sales analytics for products including supplier information and user demographics
        """
        match_stage = {}
        if start_date or end_date:
            match_stage["sales.purchase_date"] = {}
            if start_date:
                match_stage["sales.purchase_date"]["$gte"] = start_date
            if end_date:
                match_stage["sales.purchase_date"]["$lte"] = end_date

        pipeline = [
            {"$lookup": {
                "from": "purchases",
                "localField": "_id",
                "foreignField": "product_id",
                "as": "sales"
            }},
            {"$lookup": {
                "from": "suppliers",
                "localField": "supplier_id",
                "foreignField": "_id",
                "as": "supplier"
            }},
            {"$unwind": "$supplier"},
            {"$unwind": "$sales"},
            {"$match": match_stage},
            {"$lookup": {
                "from": "users",
                "localField": "sales.user_id",
                "foreignField": "_id",
                "as": "buyer"
            }},
            {"$unwind": "$buyer"},
            {"$group": {
                "_id": {
                    "product_id": "$_id",
                    "product_name": "$name",
                    "supplier_name": "$supplier.name"
                },
                "total_sales": {"$sum": 1},
                "total_quantity": {"$sum": "$sales.quantity"},
                "total_revenue": {
                    "$sum": {"$multiply": ["$price", "$sales.quantity"]}
                },
                "average_quantity_per_sale": {"$avg": "$sales.quantity"},
                "unique_customers": {"$addToSet": "$buyer._id"},
                "sales_by_month": {
                    "$push": {
                        "month": {"$month": "$sales.purchase_date"},
                        "year": {"$year": "$sales.purchase_date"},
                        "quantity": "$sales.quantity",
                        "date": "$sales.purchase_date"
                    }
                }
            }},
            {"$project": {
                "_id": 0,
                "product_id": {"$toString": "$_id.product_id"},
                "product_name": "$_id.product_name",
                "supplier_name": "$_id.supplier_name",
                "total_sales": 1,
                "total_quantity": 1,
                "total_revenue": 1,
                "average_quantity_per_sale": 1,
                "unique_customers_count": {"$size": "$unique_customers"},
                "sales_by_month": {
                    "$map": {
                        "input": "$sales_by_month",
                        "as": "sale",
                        "in": {
                            "month": "$$sale.month",
                            "year": "$$sale.year",
                            "quantity": "$$sale.quantity",
                            "date": "$$sale.date"
                        }
                    }
                }
            }},
            {"$sort": {"total_revenue": -1}}
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)
        
        # Ensure all ObjectId fields are converted to strings
        for result in results:
            if "unique_customers" in result:
                result["unique_customers"] = [str(id) for id in result["unique_customers"]]
        
        return results
