from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import hash_password


from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import Token
from app.security import create_access_token, verify_password

from app.deps import CurrentUser

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