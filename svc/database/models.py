import uuid

from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import UUID

from svc.database.base import Base


class Wallet(Base):
    """
    Модель кошелька пользователя.

    Хранит информацию о балансе кошелька с уникальным идентификатором.
    """
    __tablename__ = "wallets"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    balance = Column(Numeric(precision=20, scale=2), default=0, nullable=False)

    def __repr__(self) -> str:
        return f"<Wallet(id={self.id}, balance={self.balance})>"

