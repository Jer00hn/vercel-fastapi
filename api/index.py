import os
import time
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("subscription_server")

app = FastAPI(
    title="Subscription Management API",
    description="Асинхронный сервис проверки подписок (Hash/HSET)"
)

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")

SUBS_KEY = "subscriptions"


class SubscriptionRequest(BaseModel):
    username: str
    days: int


async def call_upstash(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        logger.error("❌ Не заданы переменные UPSTASH_URL или UPSTASH_TOKEN!")
        raise HTTPException(status_code=500, detail="Server configuration error")

    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                UPSTASH_URL, 
                json=list(args), 
                headers=headers, 
                timeout=5.0
            )
            response.raise_for_status()
            return response.json().get("result")
        except httpx.HTTPError as e:
            logger.error(f"❌ Ошибка обращения к Upstash Redis: {e}")
            raise HTTPException(status_code=502, detail="Database connection error")


# =====================================================================
# 1. ПУБЛИЧНЫЙ ЭНДПОИНТ
# =====================================================================

@app.get("/check/{username}")
async def check_subscription(username: str):
    logger.info(f"Запрос проверки подписки для: {username}")
    
    # Заменяем ZSCORE на HGET
    score = await call_upstash("HGET", SUBS_KEY, username)

    if score is None:
        logger.info(f"Пользователь '{username}' не найден в хэше.")
        return {"active": False, "expiry": None}

    expiry_timestamp = float(score)

    if time.time() >= expiry_timestamp:
        logger.info(f"Подписка для '{username}' истекла.")
        return {"active": False, "expiry": None}

    expiry_dt = datetime.fromtimestamp(expiry_timestamp)
    expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info(f"У пользователя '{username}' активна подписка до {expiry_str}")
    return {
        "active": True,
        "expiry": expiry_str
    }


# =====================================================================
# 2. АДМИНСКИЕ ЭНДПОИНТЫ
# =====================================================================

def verify_admin(x_admin_key: str):
    if not ADMIN_SECRET_KEY or x_admin_key != ADMIN_SECRET_KEY:
        logger.warning("⚠️ Несанкционированная попытка доступа к админ-панели!")
        raise HTTPException(
            status_code=401, 
            detail="Unauthorized: Incorrect or missing X-Admin-Key header"
        )


@app.post("/admin/add")
async def add_subscription(
    req: SubscriptionRequest, 
    x_admin_key: str = Header(None)
):
    verify_admin(x_admin_key)

    expiry_dt = datetime.now() + timedelta(days=req.days)
    expiry_timestamp = int(expiry_dt.timestamp())

    # HSET key field value -> HSET subscriptions username timestamp
    await call_upstash("HSET", SUBS_KEY, req.username, expiry_timestamp)

    expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"✅ Выдана подписка для '{req.username}' на {req.days} дн. (до {expiry_str})")

    return {
        "status": "success",
        "username": req.username,
        "days_added": req.days,
        "expiry": expiry_str
    }


@app.delete("/admin/remove/{username}")
async def remove_subscription(username: str, x_admin_key: str = Header(None)):
    verify_admin(x_admin_key)

    # Заменяем ZREM на HDEL
    removed_count = await call_upstash("HDEL", SUBS_KEY, username)

    if removed_count:
        logger.info(f"❌ Подписка пользователя '{username}' была удалена.")
        return {"status": "success", "message": f"Пользователь '{username}' удален."}
    
    return {"status": "not_found", "message": f"Пользователь '{username}' не найден в базе."}
    
