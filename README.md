```
  ___ ___ ___ _____     _   ___ ___  __      ___   _    _    ___ _____ ___ 
 | _ \ __/ __|_   _|   /_\ | _ \_ _| \ \    / /_\ | |  | |  | __|_   _/ __|
 |   / _|\__ \ | |    / _ \|  _/| |   \ \/\/ / _ \| |__| |__| _|  | | \__ \
 |_|_\___|___/ |_|   /_/ \_\_| |___|   \_/\_/_/ \_\____|____|___| |_| |___/
                                                                           
```

# REST API для работы с кошельками пользователей

REST API для управления кошельками пользователей с поддержкой операций пополнения и снятия средств.

## Требования

Для запуска приложения необходимо установить:

- **Python** версии 3.9 или выше
- **PostgreSQL** версии 15 или выше
- **uv** - современный менеджер пакетов Python (рекомендуется)

### Установка зависимостей

#### Установка Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.9 python3-pip python3-venv
```

**macOS:**
```bash
brew install python@3.9
```

**Windows:**
Скачайте установщик с [python.org](https://www.python.org/downloads/)

#### Установка PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Скачайте установщик с [postgresql.org](https://www.postgresql.org/download/windows/)

#### Установка uv

**Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Или через pip:
```bash
pip install uv
```

## Локальный запуск

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd REST_API_for_working_with_user_wallets
```

### 2. Настройка базы данных

Создайте базу данных и пользователя в PostgreSQL:

```bash
sudo -u postgres psql
```

В консоли PostgreSQL выполните:

```sql
CREATE DATABASE wallet_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE wallet_db TO postgres;
\q
```

### 3. Установка зависимостей

Используя uv (рекомендуется):

```bash
uv sync
```

Или используя pip:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# или
.venv\Scripts\activate  # Windows

pip install -e .
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта (опционально):

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db
```

Или экспортируйте переменную окружения:

```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/wallet_db"
```

### 5. Применение миграций

```bash
cd svc
uv run alembic upgrade head
# или
alembic upgrade head
```

### 6. Запуск приложения

Используя uv:

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Или используя uvicorn напрямую:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Или используя gunicorn для production:

```bash
gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:8080
```

Приложение будет доступно по адресу: `http://localhost:8080`

## Запуск через Docker

### Требования

- **Docker** версии 20.10 или выше
- **Docker Compose** версии 2.0 или выше

### Установка Docker

**Ubuntu/Debian:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**macOS:**
Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop)

**Windows:**
Скачайте [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Запуск

1. Соберите и запустите контейнеры:

```bash
docker-compose up --build
```

2. Приложение будет доступно по адресу: `http://localhost:8080`

3. Для запуска в фоновом режиме:

```bash
docker-compose up -d
```

4. Просмотр логов:

```bash
docker-compose logs -f app
```

5. Остановка контейнеров:

```bash
docker-compose down
```

## API Документация

После запуска приложения доступна интерактивная документация:

- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Примеры использования API

API предоставляет следующие эндпоинты для работы с кошельками:

- **POST** `/api/v1/wallets` - Создать новый кошелек
- **GET** `/api/v1/wallets/{wallet_id}` - Получить баланс кошелька
- **POST** `/api/v1/wallets/{wallet_id}/operation` - Выполнить операцию (пополнение/снятие)

### Получить информацию о сервисе

```bash
curl http://localhost:8080/api/v1/wallets/
```

### Создать новый кошелек

Создать кошелек с начальным балансом:

```bash
curl -X POST http://localhost:8080/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{
    "initial_balance": "1000.00"
  }'
```

Ответ:
```json
{
  "wallet_id": "123e4567-e89b-12d3-a456-426614174000",
  "balance": "1000.00"
}
```

Создать кошелек с нулевым балансом (по умолчанию):

```bash
curl -X POST http://localhost:8080/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{}'
```

### Получить баланс кошелька

```bash
curl http://localhost:8080/api/v1/wallets/{wallet_id}
```

Пример:
```bash
curl http://localhost:8080/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000
```

### Пополнить кошелек

```bash
curl -X POST http://localhost:8080/api/v1/wallets/{wallet_id}/operation \
  -H "Content-Type: application/json" \
  -d '{
    "operation_type": "DEPOSIT",
    "amount": "100.50"
  }'
```

### Снять средства с кошелька

```bash
curl -X POST http://localhost:8080/api/v1/wallets/{wallet_id}/operation \
  -H "Content-Type: application/json" \
  -d '{
    "operation_type": "WITHDRAW",
    "amount": "50.25"
  }'
```

## Пример полного цикла работы с кошельком

```bash
# 1. Создать новый кошелек с начальным балансом 1000.00
WALLET_ID=$(curl -s -X POST http://localhost:8080/api/v1/wallets \
  -H "Content-Type: application/json" \
  -d '{"initial_balance": "1000.00"}' | jq -r '.wallet_id')

echo "Создан кошелек: $WALLET_ID"

# 2. Проверить баланс кошелька
curl http://localhost:8080/api/v1/wallets/$WALLET_ID

# 3. Пополнить кошелек на 500.00
curl -X POST http://localhost:8080/api/v1/wallets/$WALLET_ID/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "DEPOSIT", "amount": "500.00"}'

# 4. Проверить баланс после пополнения
curl http://localhost:8080/api/v1/wallets/$WALLET_ID

# 5. Снять средства с кошелька (200.00)
curl -X POST http://localhost:8080/api/v1/wallets/$WALLET_ID/operation \
  -H "Content-Type: application/json" \
  -d '{"operation_type": "WITHDRAW", "amount": "200.00"}'

# 6. Проверить финальный баланс
curl http://localhost:8080/api/v1/wallets/$WALLET_ID
```

## Структура проекта

```
REST_API_for_working_with_user_wallets/
├── main.py                 # Точка входа приложения
├── pyproject.toml          # Конфигурация проекта и зависимости
├── uv.lock                 # Lock-файл зависимостей
├── Dockerfile              # Конфигурация Docker образа
├── docker-compose.yml      # Конфигурация Docker Compose
├── README.md               # Документация
└── svc/                    # Основной пакет приложения
    ├── main.py             # Альтернативная точка входа
    ├── routes/              # API роуты
    │   └── wallets.py      # Роуты для работы с кошельками
    ├── database/            # Работа с базой данных
    │   ├── base.py          # Настройка подключения к БД
    │   └── models.py        # Модели данных
    ├── schemas.py           # Pydantic схемы
    ├── core/                # Основные утилиты
    │   └── logger.py        # Настройка логирования
    ├── migrations/          # Миграции базы данных
    │   └── env.py          # Конфигурация Alembic
    └── tests/               # Тесты
        └── test_wallets.py  # Тесты API кошельков
```

## Тестирование

Запуск тестов:

```bash
uv run pytest
# или
pytest
```

## Разработка

### Создание новой миграции

```bash
cd svc
uv run alembic revision --autogenerate -m "Описание миграции"
```

### Применение миграций

```bash
cd svc
uv run alembic upgrade head
```

### Откат миграции

```bash
cd svc
uv run alembic downgrade -1
```

## Технологии

- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - система миграций базы данных
- **PostgreSQL** - реляционная база данных
- **Pydantic** - валидация данных
- **uvicorn** - ASGI сервер
- **gunicorn** - WSGI HTTP сервер
- **uv** - быстрый менеджер пакетов Python
