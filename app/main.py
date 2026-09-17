from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import AccountResponse, AmountRequest, TransferRequest, UserCreate, UserResponse
from app.security import hash_password


from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import Token
from app.security import create_access_token, verify_password

from app.deps import CurrentUser

from app.models import Account

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload : UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalars().first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    
    new_user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    
    token = create_access_token(user.id)
    return Token(access_token=token, token_type="bearer")

@app.get("/me", response_model=UserResponse)
async def read_current_user(current_user: CurrentUser):
    return current_user

@app.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def open_account(current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_account = Account(owner_id=current_user.id)
    db.add(new_account)
    await db.commit()
    await db.refresh(new_account)
    return new_account

@app.post("/accounts/{account_id}/deposit", response_model=AccountResponse)
async def deposit(
    account_id: int,
    payload: AmountRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
    if account.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This isn't your account")
    
    account.balance += payload.amount
    await db.commit()
    await db.refresh(account)
    return account

@app.post("/accounts/{account_id}/withdraw", response_model=AccountResponse)
async def withdraw(
    account_id: int,
    payload: AmountRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()
    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")
    if account.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This isn't your account")
    if account.balance < payload.amount:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient funds")
    
    account.balance -= payload.amount
    await db.commit()
    await db.refresh(account)
    return account

@app.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    account = result.scalars().first()

    if account is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")

    if account.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This isn't your account")

    return account

@app.post("/accounts/{account_id}/transfer", response_model=AccountResponse)
async def transfer(
    account_id: int,
    payload: TransferRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Account).where(Account.id == account_id))
    sender = result.scalars().first()

    if sender is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Account not found")

    if sender.owner_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This isn't your account")

    result = await db.execute(select(Account).where(Account.id == payload.to_account_id))
    receiver = result.scalars().first()

    if receiver is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Receiving account not found")

    if sender.balance < payload.amount:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient funds")

    sender.balance -= payload.amount
    receiver.balance += payload.amount

    await db.commit()
    await db.refresh(sender)

    return sender