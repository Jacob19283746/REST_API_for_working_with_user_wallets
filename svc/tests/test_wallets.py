import os
import uuid

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

import pytest
from decimal import Decimal
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from main import create_app
from svc.database.base import Base, get_session
from svc.database.models import Wallet


# Настройка тестовой базы данных
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="function")
async def db_session():
    """Фикстура для создания тестовой сессии БД."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def override_get_session(test_session: AsyncSession):
    """Переопределение зависимости для тестовой сессии."""
    async def _get_session():
        try:
            yield test_session
            await test_session.commit()
        except Exception:
            await test_session.rollback()
            raise
    return _get_session


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession):
    """Фикстура для создания тестового клиента."""
    app = create_app()
    app.dependency_overrides[get_session] = override_get_session(db_session)
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_home_endpoint(client: AsyncClient):
    """Тест главной страницы API."""
    response = await client.get("/api/v1/wallets/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data
    assert data["message"] == "Welcome to the Wallet API"


@pytest.mark.asyncio
async def test_get_all_wallets_empty(client: AsyncClient):
    """Тест получения всех кошельков когда их нет."""
    response = await client.get("/api/v1/wallets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_create_wallet_default_balance(client: AsyncClient, db_session: AsyncSession):
    """Тест создания кошелька с балансом по умолчанию (0)."""
    response = await client.post("/api/v1/wallets", json={})
    assert response.status_code == 201
    data = response.json()
    assert "wallet_id" in data
    assert "balance" in data
    assert Decimal(data["balance"]) == Decimal("0")


@pytest.mark.asyncio
async def test_create_wallet_with_initial_balance(client: AsyncClient, db_session: AsyncSession):
    """Тест создания кошелька с начальным балансом."""
    response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "1000.50"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "wallet_id" in data
    assert Decimal(data["balance"]) == Decimal("1000.50")


@pytest.mark.asyncio
async def test_get_wallet_balance(client: AsyncClient, db_session: AsyncSession):
    """Тест получения баланса существующего кошелька."""
    # Создаем кошелек
    create_response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "500.00"}
    )
    assert create_response.status_code == 201
    wallet_id = create_response.json()["wallet_id"]
    
    # Получаем баланс
    response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert Decimal(data["balance"]) == Decimal("500.00")


@pytest.mark.asyncio
async def test_get_wallet_balance_not_found(client: AsyncClient):
    """Тест получения баланса несуществующего кошелька."""
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/v1/wallets/{fake_id}")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_deposit_operation(client: AsyncClient, db_session: AsyncSession):
    """Тест операции пополнения кошелька."""
    # Создаем кошелек
    create_response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "100.00"}
    )
    wallet_id = create_response.json()["wallet_id"]
    
    # Пополняем кошелек
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "50.25"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert Decimal(data["balance"]) == Decimal("150.25")


@pytest.mark.asyncio
async def test_withdraw_operation(client: AsyncClient, db_session: AsyncSession):
    """Тест операции снятия средств с кошелька."""
    # Создаем кошелек
    create_response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "200.00"}
    )
    wallet_id = create_response.json()["wallet_id"]
    
    # Снимаем средства
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "75.50"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["wallet_id"] == wallet_id
    assert Decimal(data["balance"]) == Decimal("124.50")


@pytest.mark.asyncio
async def test_withdraw_insufficient_funds(client: AsyncClient, db_session: AsyncSession):
    """Тест снятия средств при недостаточном балансе."""
    # Создаем кошелек
    create_response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "50.00"}
    )
    wallet_id = create_response.json()["wallet_id"]
    
    # Пытаемся снять больше, чем есть
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "100.00"}
    )
    assert response.status_code == 400
    assert "insufficient funds" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_operation_wallet_not_found(client: AsyncClient):
    """Тест операции с несуществующим кошельком."""
    fake_id = str(uuid.uuid4())
    response = await client.post(
        f"/api/v1/wallets/{fake_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.00"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_multiple_operations(client: AsyncClient, db_session: AsyncSession):
    """Тест нескольких операций подряд."""
    # Создаем кошелек
    create_response = await client.post(
        "/api/v1/wallets",
        json={"initial_balance": "1000.00"}
    )
    wallet_id = create_response.json()["wallet_id"]
    
    # Пополняем
    deposit_response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": "200.00"}
    )
    assert deposit_response.status_code == 200
    assert Decimal(deposit_response.json()["balance"]) == Decimal("1200.00")
    
    # Снимаем
    withdraw_response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": "300.00"}
    )
    assert withdraw_response.status_code == 200
    assert Decimal(withdraw_response.json()["balance"]) == Decimal("900.00")
    
    # Проверяем финальный баланс
    balance_response = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert balance_response.status_code == 200
    assert Decimal(balance_response.json()["balance"]) == Decimal("900.00")


@pytest.mark.asyncio
async def test_get_all_wallets_with_data(client: AsyncClient, db_session: AsyncSession):
    """Тест получения всех кошельков когда они есть."""
    # Создаем несколько кошельков
    wallet1 = await client.post("/api/v1/wallets", json={"initial_balance": "100.00"})
    wallet2 = await client.post("/api/v1/wallets", json={"initial_balance": "200.00"})
    wallet3 = await client.post("/api/v1/wallets", json={"initial_balance": "0.00"})
    
    # Получаем все кошельки (только с балансом > 0)
    response = await client.get("/api/v1/wallets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Должны быть только кошельки с балансом > 0
    assert len(data) >= 2
    balances = [Decimal(w["balance"]) for w in data]
    assert Decimal("100.00") in balances
    assert Decimal("200.00") in balances
