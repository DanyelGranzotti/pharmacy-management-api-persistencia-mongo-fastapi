from typing import Dict, Any, List
from bson import ObjectId
from app.models.supplier import SupplierModel
from app.models.common import PaginationParams
from app.config.database import database
from app.utils.mongo_utils import convert_mongo_document
from datetime import datetime
from fastapi import HTTPException


class SupplierRepository:
    collection = database.suppliers

    async def create(self, supplier: SupplierModel) -> str:
        result = await self.collection.insert_one(supplier.model_dump())
        return str(result.inserted_id)

    async def get_by_id(self, id: str) -> Dict[str, Any]:
        document = await self.collection.find_one({"_id": ObjectId(id)})
        return convert_mongo_document(document)

    async def get_all(self, pagination: PaginationParams, filters: Dict = None):
        skip = (pagination.page - 1) * pagination.limit
        
        query = filters or {}
        cursor = self.collection.find(query)

        if pagination.sort_by:
            sort_order = 1 if pagination.sort_order == "asc" else -1
            cursor = cursor.sort(pagination.sort_by, sort_order)

        total = await self.collection.count_documents(query)
        suppliers = await cursor.skip(skip).limit(pagination.limit).to_list(None)

        return {
            "total": total,
            "page": pagination.page,
            "limit": pagination.limit,
            "suppliers": [convert_mongo_document(s) for s in suppliers]
        }

    async def update(self, id: str, update_data: Dict) -> Dict[str, Any]:
        update_data["updated_at"] = datetime.utcnow()
        await self.collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": update_data}
        )
        return await self.get_by_id(id)

    async def get_supplier_products(self, supplier_id: str, pagination: PaginationParams) -> Dict:
        skip = (pagination.page - 1) * pagination.limit
        
        query = {"supplier_id": supplier_id}
        cursor = database.products.find(query)

        if pagination.sort_by:
            sort_order = 1 if pagination.sort_order == "asc" else -1
            cursor = cursor.sort(pagination.sort_by, sort_order)

        total = await database.products.count_documents(query)
        products = await cursor.skip(skip).limit(pagination.limit).to_list(None)

        return {
            "total": total,
            "page": pagination.page,
            "limit": pagination.limit,
            "products": [convert_mongo_document(p) for p in products]
        }

    async def delete(self, id: str) -> bool:
        # Verificar se existem produtos associados
        products_count = await database.products.count_documents({"supplier_id": id})
        if products_count > 0:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete supplier with associated products"
            )
            
        result = await self.collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0
