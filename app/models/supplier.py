from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SupplierModel(BaseModel):
    name: str = Field(max_length=255)
    contact_info: str = Field()
    email: str = Field(max_length=255)
    cnpj: str = Field(max_length=14)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Supplier Name",
                "contact_info": "Contact Information",
                "email": "supplier@example.com",
                "cnpj": "12345678901234"
            }
        }
    }

class UpdateSupplierModel(BaseModel):
    name: Optional[str] = None
    contact_info: Optional[str] = None
    email: Optional[str] = None
    cnpj: Optional[str] = None
