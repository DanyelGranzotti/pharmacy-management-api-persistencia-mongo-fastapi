from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserModel(BaseModel):
    email: EmailStr = Field(unique=True)
    name: str = Field(max_length=100)
    status: bool = Field(default=True)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "status": True,
                "is_active": True,
                "is_staff": False,
                "is_superuser": False
            }
        }
    }

class UpdateUserModel(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    is_active: Optional[bool] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
