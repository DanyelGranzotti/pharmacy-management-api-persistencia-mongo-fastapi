from app.models.common import PaginationParams
from typing import Dict, Any
from app.utils.mongo_utils import convert_mongo_document

class BaseRepository:
    async def paginate_and_filter(self, collection, pagination: PaginationParams, filters: Dict[str, Any] = None):
        skip = (pagination.page - 1) * pagination.limit
        
        # Build filter query
        filter_query = {}
        if filters:
            for key, value in filters.items():
                if value is not None:
                    if isinstance(value, str):
                        filter_query[key] = {"$regex": value, "$options": "i"}
                    else:
                        filter_query[key] = value

        # Build sort query
        sort_query = []
        if pagination.sort_by:
            sort_direction = 1 if pagination.sort_order == "asc" else -1
            sort_query.append((pagination.sort_by, sort_direction))

        # Execute query
        total = await collection.count_documents(filter_query)
        cursor = collection.find(filter_query)
        
        if sort_query:
            cursor = cursor.sort(sort_query)
        
        cursor = cursor.skip(skip).limit(pagination.limit)
        
        # Get results and convert documents
        results = [convert_mongo_document(doc) async for doc in cursor]

        total_pages = (total + pagination.limit - 1) // pagination.limit

        return {
            "data": results,
            "total": total,
            "page": pagination.page,
            "limit": pagination.limit,
            "total_pages": total_pages
        }
