from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends

from api_v1.wallet_users import get_wallet_users

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def index() -> dict[str, str]:
    return {
        "info": "This is the index page of fastapi. "
        "You probably want to go to 'http://<hostname:port>/docs'.",
    }


@router.get("/wallet_user/{num}", tags=["wallet_user"])
async def wallet_user(
    num: int,
) -> list[dict[str, Any]]:
    result = get_wallet_users(num)
    logger.info(f"API wallet_user: {result}")
    return result
