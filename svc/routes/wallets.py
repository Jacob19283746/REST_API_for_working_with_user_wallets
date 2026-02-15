import logging
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from svc.database.base import get_session
from svc.database.models import Wallet
from svc.schemas import (
    OperationType,
    WalletBalanceResponse,
    WalletCreateRequest,
    WalletOperationRequest,
)

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])
logger = logging.getLogger(__name__)


@router.get("/")
async def home():
    """
    Главная страница API.

    Returns:
        Страница с приветствием и ссылкой на документацию.
    """
    return {
        "message": "Welcome to the Wallet API",
        "docs": "/docs"
    }


@router.get("", response_model=list[WalletBalanceResponse])
async def get_all_wallets(
        session: AsyncSession = Depends(get_session),
        ) -> list[WalletBalanceResponse]:
    """
    Получает список всех кошельков с их текущими балансами.

    Args:
        session: Сессия базы данных.

    Returns:
        Список кошельков с их текущими балансами.
    """
    result = await session.execute(select(Wallet))
    wallets = result.scalars().all()
    return [
        WalletBalanceResponse(wallet_id=wallet.id, balance=wallet.balance)
        for wallet in wallets if wallet.balance > 0.00000001
    ]

@router.post("", response_model=WalletBalanceResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    request: WalletCreateRequest = WalletCreateRequest(),
    session: AsyncSession = Depends(get_session),
) -> WalletBalanceResponse:
    """
    Создает новый кошелек с указанным начальным балансом.

    Args:
        request: Данные для создания кошелька (начальный баланс).
        session: Сессия базы данных.

    Returns:
        Информация о созданном кошельке с начальным балансом.
    """
    wallet = Wallet(balance=request.initial_balance)
    session.add(wallet)
    await session.flush()
    await session.refresh(wallet)

    logger.info(
        f"Created wallet {wallet.id} with initial balance: {wallet.balance}"
    )

    return WalletBalanceResponse(
        wallet_id=wallet.id,
        balance=Decimal(str(wallet.balance)),
    )


@router.get("/{wallet_id}", response_model=WalletBalanceResponse)
async def get_wallet_balance(
    wallet_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> WalletBalanceResponse:
    """
    Получает текущий баланс кошелька по его идентификатору.

    Args:
        wallet_id: Уникальный идентификатор кошелька (UUID).
        session: Сессия базы данных.

    Returns:
        Информация о кошельке с текущим балансом.

    Raises:
        HTTPException: Если кошелек с указанным ID не найден (404).
    """
    result = await session.execute(
        select(Wallet).where(Wallet.id == wallet_id)
    )
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with id {wallet_id} not found",
        )

    return WalletBalanceResponse(
        wallet_id=wallet.id,
        balance=Decimal(str(wallet.balance)),
    )


@router.post("/{wallet_id}/operation")
async def wallet_operation(
    wallet_id: UUID,
    operation: WalletOperationRequest,
    session: AsyncSession = Depends(get_session),
) -> WalletBalanceResponse:
    """
    Выполняет операцию с кошельком (пополнение или снятие средств).

    Использует блокировку строки для обеспечения потокобезопасности
    при одновременных операциях.

    Args:
        wallet_id: Уникальный идентификатор кошелька (UUID).
        operation: Данные операции (тип операции и сумма).
        session: Сессия базы данных.

    Returns:
        Информация о кошельке с обновленным балансом.

    Raises:
        HTTPException: Если кошелек не найден (404), недостаточно средств (400)
                       или указан неверный тип операции (400).
    """
    result = await session.execute(
        select(Wallet)
        .where(Wallet.id == wallet_id)
        .with_for_update()
    )
    wallet = result.scalar_one_or_none()

    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wallet with id {wallet_id} not found",
        )

    current_balance = Decimal(str(wallet.balance))
    amount = operation.amount

    if operation.operation_type == OperationType.DEPOSIT:
        new_balance = current_balance + amount
    elif operation.operation_type == OperationType.WITHDRAW:
        new_balance = current_balance - amount
        if new_balance < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid operation type",
        )

    wallet.balance = new_balance
    # Сессия будет зафиксирована автоматически с помощью зависимости get_session

    logger.info(
        f"Wallet {wallet_id}: {operation.operation_type} "
        f"{amount}, new balance: {new_balance}"
    )

    return WalletBalanceResponse(
        wallet_id=wallet.id,
        balance=new_balance,
    )

