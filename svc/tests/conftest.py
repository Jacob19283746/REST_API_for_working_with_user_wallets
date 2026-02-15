import os
import sys

# Устанавливаем тестовую БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Перезагружаем модули базы данных, если они уже были импортированы
if "svc.database.base" in sys.modules:
    import importlib
    importlib.reload(sys.modules["svc.database.base"])

