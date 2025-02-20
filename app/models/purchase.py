from typing import Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from app.utils.validators import validate_object_id

class PurchaseModel(BaseModel):
    user_id: str = Field()
    product_id: str = Field()
    quantity: int = Field(gt=0)
    purchase_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('user_id', 'product_id')
    def validate_object_ids(cls, v):
        return validate_object_id(v)

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "product_id": "507f1f77bcf86cd799439012",
                "quantity": 1,
            }
        }
    }

class UpdatePurchaseModel(BaseModel):
    quantity: Optional[int] = None
