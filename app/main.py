from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.security import hash_password

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

