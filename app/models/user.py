from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class BankAccountModel(BaseModel):
    account_number: str = Field(max_length=20)
    bank_name: str = Field(max_length=100)
    branch_code: str = Field(max_length=10)
    account_type: str = Field(max_length=50)
    balance: float = Field(default=0.0)

class UserModel(BaseModel):
    email: EmailStr = Field(unique=True)
    name: str = Field(max_length=100)
    status: bool = Field(default=True)
    is_active: bool = Field(default=True)
    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    bank_account: BankAccountModel
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
                "is_superuser": False,
                "bank_account": {
                    "account_number": "123456",
                    "bank_name": "Example Bank",
                    "branch_code": "001",
                    "account_type": "Checking",
                    "balance": 1000.0
                }
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
    bank_account: Optional[BankAccountModel] = None
