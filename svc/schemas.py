from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """
    Типы операций с кошельком.

    Attributes:
        DEPOSIT: Пополнение кошелька (увеличение баланса).
        WITHDRAW: Снятие средств с кошелька (уменьшение баланса).
    """
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperationRequest(BaseModel):
    """
    Модель запроса на выполнение операции с кошельком.

    Attributes:
        operation_type: Тип операции (пополнение или снятие).
        amount: Сумма операции (должна быть больше нуля).
    """

    operation_type: OperationType = Field(..., description="Тип операции")
    amount: Decimal = Field(..., gt=0, description="Сумма операции")


class WalletCreateRequest(BaseModel):
    """
    Модель запроса на создание нового кошелька.

    Attributes:
        initial_balance: Начальный баланс кошелька (по умолчанию 0).
    """

    initial_balance: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Начальный баланс кошелька"
    )


class WalletBalanceResponse(BaseModel):
    """
    Модель ответа с информацией о балансе кошелька.

    Attributes:
        wallet_id: Уникальный идентификатор кошелька.
        balance: Текущий баланс кошелька.
    """

    wallet_id: UUID = Field(..., description="Wallet UUID")
    balance: Decimal = Field(..., description="Current balance")

    class Config:
        """
        Конфигурация Pydantic модели.

        Настраивает сериализацию Decimal в строку для корректной
        передачи через JSON API.
        """

        json_encoders = {Decimal: str}

