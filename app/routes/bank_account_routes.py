from fastapi import APIRouter, HTTPException
from app.repositories.user_repository import UserRepository

router = APIRouter()
user_repository = UserRepository()

@router.get("/users/{user_id}/bank-account", response_description="Get user bank account")
async def get_bank_account(user_id: str):
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    bank_account = await user_repository.get_bank_account(user_id)
    if not bank_account:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    return bank_account

@router.put("/users/{user_id}/bank-account/balance", response_description="Update bank account balance")
async def update_bank_balance(user_id: str, new_balance: float):
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Balance cannot be negative")
    
    updated_user = await user_repository.update_bank_balance(user_id, new_balance)
    return updated_user["bank_account"]

@router.post("/users/{user_id}/bank-account/deposit", response_description="Make a deposit")
async def make_deposit(user_id: str, amount: float):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")
    
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await user_repository.deposit(user_id, amount)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Bank account not found")
    
    return {
        "message": f"Successfully deposited {amount}",
        "bank_account": updated_user["bank_account"]
    }
