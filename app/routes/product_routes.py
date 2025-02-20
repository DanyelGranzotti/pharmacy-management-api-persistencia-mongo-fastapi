from fastapi import APIRouter, HTTPException, Query
from app.models.product import ProductModel, UpdateProductModel
from app.repositories.product_repository import ProductRepository
from app.models.common import PaginationParams
from typing import Optional

router = APIRouter()
product_repository = ProductRepository()

@router.post("/products/", response_description="Create a new product")
async def create_product(product: ProductModel):
    product_id = await product_repository.create(product)
    return {"_id": product_id}

@router.get("/products/", response_description="List all products")
async def list_products(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    supplier_id: Optional[str] = None
):
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    filters = {
        "name": name,
        "supplier_id": supplier_id
    }
    
    if min_price is not None:
        filters["cost_price"] = {"$gte": min_price}
    if max_price is not None:
        filters.setdefault("cost_price", {})["$lte"] = max_price

    return await product_repository.get_all(pagination, filters)

@router.get("/products/{id}", response_description="Get a product by id")
async def get_product(id: str):
    product = await product_repository.get_by_id(id)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Product not found")

@router.put("/products/{id}", response_description="Update a product")
async def update_product(id: str, product: UpdateProductModel):
    existing_product = await product_repository.get_by_id(id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {k: v for k, v in product.dict(exclude_unset=True).items()}
    updated_product = await product_repository.update(id, update_data)
    return updated_product

@router.delete("/products/{id}", response_description="Delete a product")
async def delete_product(id: str):
    existing_product = await product_repository.get_by_id(id)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await product_repository.delete(id)
    return {"message": "Product deleted successfully"}
