from fastapi import APIRouter, HTTPException, Query
from app.models.purchase import PurchaseModel, UpdatePurchaseModel
from app.repositories.purchase_repository import PurchaseRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.models.common import PaginationParams
from typing import Optional

router = APIRouter()
purchase_repository = PurchaseRepository()
product_repository = ProductRepository()
user_repository = UserRepository()

@router.post("/purchases/", response_description="Create a new purchase")
async def create_purchase(purchase: PurchaseModel):
    user = await user_repository.get_by_id(purchase.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    product = await product_repository.get_by_id(purchase.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["quantity"] < purchase.quantity:
        raise HTTPException(status_code=400, detail="Insufficient product quantity")
    
    cost = product["price"] * purchase.quantity

    if not user.get("bank_account"):
        raise HTTPException(status_code=404, detail="User has no bank account")
    
    if user["bank_account"]["balance"] < cost:
        raise HTTPException(status_code=400, detail="Insufficient funds in bank account")
    
    new_balance = user["bank_account"]["balance"] - cost
    await user_repository.update_bank_balance(purchase.user_id, new_balance)
    
    new_quantity = product["quantity"] - purchase.quantity
    await product_repository.update(purchase.product_id, {"quantity": new_quantity})

    purchase_id = await purchase_repository.create(purchase)
    await user_repository.add_purchased_product(purchase.user_id, purchase.product_id)
    
    return {"_id": purchase_id}

@router.get("/purchases/", response_description="List all purchases")
async def list_purchases(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    user_id: Optional[str] = None
):
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    filters = {}
    if user_id:
        filters["user_id"] = user_id

    return await purchase_repository.get_all(pagination, filters)

@router.get("/purchases/{id}", response_description="Get a purchase by id")
async def get_purchase(id: str):
    purchase = await purchase_repository.get_by_id(id)
    if purchase:
        return purchase
    raise HTTPException(status_code=404, detail="Purchase not found")

@router.put("/purchases/{id}", response_description="Update a purchase")
async def update_purchase(id: str, purchase: UpdatePurchaseModel):
    existing_purchase = await purchase_repository.get_by_id(id)
    if not existing_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    if purchase.quantity is not None:
        product = await product_repository.get_by_id(existing_purchase["product_id"])
        quantity_diff = purchase.quantity - existing_purchase["quantity"]
        
        if product["quantity"] < quantity_diff:
            raise HTTPException(status_code=400, detail="Insufficient product quantity")
        
        new_quantity = product["quantity"] - quantity_diff
        await product_repository.update(existing_purchase["product_id"], {"quantity": new_quantity})
    
    update_data = {k: v for k, v in purchase.dict(exclude_unset=True).items()}
    updated_purchase = await purchase_repository.update(id, update_data)
    return updated_purchase

@router.delete("/purchases/{id}", response_description="Delete a purchase")
async def delete_purchase(id: str):
    existing_purchase = await purchase_repository.get_by_id(id)
    if not existing_purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    
    product = await product_repository.get_by_id(existing_purchase["product_id"])
    new_quantity = product["quantity"] + existing_purchase["quantity"]
    await product_repository.update(existing_purchase["product_id"], {"quantity": new_quantity})
    
    await user_repository.remove_purchased_product(
        existing_purchase["user_id"], 
        existing_purchase["product_id"]
    )
    
    await purchase_repository.delete(id)
    return {"message": "Purchase deleted successfully"}
