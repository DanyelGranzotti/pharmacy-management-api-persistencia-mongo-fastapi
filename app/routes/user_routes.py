from fastapi import APIRouter, HTTPException, Query
from app.models.user import UserModel, UpdateUserModel
from app.repositories.user_repository import UserRepository
from app.repositories.product_repository import ProductRepository
from app.models.common import PaginationParams
from typing import Optional

router = APIRouter()
user_repository = UserRepository()
product_repository = ProductRepository()

@router.post("/users/", response_description="Create a new user")
async def create_user(user: UserModel):
    existing_user = await user_repository.get_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = await user_repository.create(user)
    return {"_id": user_id}

@router.get("/users/", response_description="List all users")
async def list_users(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await user_repository.get_all(pagination)

@router.get("/users/{id}", response_description="Get a user by id")
async def get_user(id: str):
    user = await user_repository.get_by_id(id)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{id}", response_description="Update a user")
async def update_user(id: str, user: UpdateUserModel):
    existing_user = await user_repository.get_by_id(id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {k: v for k, v in user.dict(exclude_unset=True).items()}
    updated_user = await user_repository.update(id, update_data)
    return updated_user

@router.delete("/users/{id}", response_description="Delete a user")
async def delete_user(id: str):
    existing_user = await user_repository.get_by_id(id)
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await user_repository.delete(id)
    return {"message": "User deleted successfully"}

@router.get("/users/{id}/purchased-products", response_description="Get all products purchased by user")
async def get_user_purchased_products(
    id: str,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    user = await user_repository.get_by_id(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

    purchased_products = await user_repository.get_purchased_products(id, pagination)
    return purchased_products