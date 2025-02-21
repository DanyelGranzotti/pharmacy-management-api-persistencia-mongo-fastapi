from fastapi import APIRouter
from app.config.database import database

router = APIRouter()

@router.get("/stats/collections", response_description="Get collection statistics")
async def get_collections_stats():
    collections = {
        "users": database.users,
        "bank_accounts": database.bank_accounts,
        "products": database.products,
        "suppliers": database.suppliers,
        "purchases": database.purchases
    }
    
    stats = {}
    for name, collection in collections.items():
        count = await collection.count_documents({})
        stats[name] = count
    
    return {
        "collection_counts": stats,
        "total_documents": sum(stats.values())
    }
