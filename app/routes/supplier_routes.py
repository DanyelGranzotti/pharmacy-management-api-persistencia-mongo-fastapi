from fastapi import APIRouter, HTTPException, Query
from app.models.supplier import SupplierModel, UpdateSupplierModel
from app.repositories.supplier_repository import SupplierRepository
from app.models.common import PaginationParams
from typing import Optional

router = APIRouter()
supplier_repository = SupplierRepository()

@router.post("/suppliers/", response_description="Create a new supplier")
async def create_supplier(supplier: SupplierModel):
    supplier_id = await supplier_repository.create(supplier)
    return {"_id": supplier_id}

@router.get("/suppliers/", response_description="List all suppliers")
async def list_suppliers(
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc",
    name: Optional[str] = None,
    email: Optional[str] = None,
    cnpj: Optional[str] = None
):
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    filters = {}
    if name:
        filters["name"] = {"$regex": name, "$options": "i"}
    if email:
        filters["email"] = email
    if cnpj:
        filters["cnpj"] = cnpj

    return await supplier_repository.get_all(pagination, filters)

@router.get("/suppliers/{id}", response_description="Get a supplier by id")
async def get_supplier(id: str):
    supplier = await supplier_repository.get_by_id(id)
    if supplier:
        return supplier
    raise HTTPException(status_code=404, detail="Supplier not found")

@router.get("/suppliers/{id}/products", response_description="Get all products from a supplier")
async def get_supplier_products(
    id: str,
    page: int = Query(1, gt=0),
    limit: int = Query(10, gt=0),
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "asc"
):
    supplier = await supplier_repository.get_by_id(id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    pagination = PaginationParams(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    return await supplier_repository.get_supplier_products(id, pagination)

@router.put("/suppliers/{id}", response_description="Update a supplier")
async def update_supplier(id: str, supplier: UpdateSupplierModel):
    existing_supplier = await supplier_repository.get_by_id(id)
    if not existing_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    update_data = {k: v for k, v in supplier.dict(exclude_unset=True).items()}
    updated_supplier = await supplier_repository.update(id, update_data)
    return updated_supplier

@router.delete("/suppliers/{id}", response_description="Delete a supplier")
async def delete_supplier(id: str):
    existing_supplier = await supplier_repository.get_by_id(id)
    if not existing_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    await supplier_repository.delete(id)
    return {"message": "Supplier deleted successfully"}
