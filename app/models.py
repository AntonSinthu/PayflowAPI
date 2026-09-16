from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

import enum
from decimal import Decimal
from sqlalchemy import Enum as SAEnum, ForeignKey, Numeric
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    accounts: Mapped[list["Account"]] = relationship(back_populates="owner")
    
class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=19, scale=4), default=0)
    status: Mapped[AccountStatus] = mapped_column(SAEnum(AccountStatus), default=AccountStatus.ACTIVE)
    
    owner: Mapped[User] = relationship(back_populates="accounts")