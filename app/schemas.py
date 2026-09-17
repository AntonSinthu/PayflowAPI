from pydantic import BaseModel, ConfigDict, EmailStr, Field

from decimal import Decimal
from app.models import AccountStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes= True)
    
    email: EmailStr
    id: int 
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    balance: Decimal
    status: AccountStatus
    
class AmountRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    
class TransferRequest(BaseModel):
    to_account_id: int
    amount: Decimal = Field(gt=0)