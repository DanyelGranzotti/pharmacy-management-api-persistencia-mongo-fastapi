from typing import Optional
from pydantic import BaseModel, Field, computed_field, validator
from datetime import datetime
from bson import ObjectId, errors

class ProductModel(BaseModel):
    name: str = Field(max_length=255)
    description: str = Field()
    cost_price: float = Field(gt=0)
    profit_margin: float = Field(default=0.20)
    quantity: int = Field(ge=0)
    supplier_id: str = Field(description="Reference to the supplier's ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @computed_field
    def price(self) -> float:
        return self.cost_price * (1 + self.profit_margin)
    
    @validator('supplier_id')
    def validate_supplier_id(cls, v):
        try:
            ObjectId(v)
            return v
        except errors.InvalidId:
            raise ValueError("Invalid supplier ID format")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Product Name",
                "description": "Product Description",
                "cost_price": 25.00,
                "profit_margin": 0.20,
                "quantity": 100,
                "supplier_id": "supplier_id_here"
            }
        }
    }

class UpdateProductModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cost_price: Optional[float] = None
    profit_margin: Optional[float] = None
    quantity: Optional[int] = None
    supplier_id: Optional[str] = None
