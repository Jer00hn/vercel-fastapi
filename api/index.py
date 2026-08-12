import os
import logging
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx


# ============================================================
# ЛОГИРОВАНИЕ
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("subscription_server")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Subscription Management API",
    description="Защищенный сервис проверки и управления подписками"
)


# ============================================================
# ENV
# ============================================================

UPSTASH_URL = os.getenv("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY")

USER_KEY = "user:"
EXPIRY_INDEX = "expiry_index"


# ============================================================
# Pydantic модель
# ============================================================

class SubscriptionRequest(BaseModel):
    username: str
    days: int


# ============================================================
# Создание httpx клиента один раз
# ============================================================

@app.on_event("startup")
async def startup_event():
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        logger.error("❌ UPSTASH_URL / UPSTASH_TOKEN не заданы!")
        raise RuntimeError("Missing Upstash configuration")

    app.state.http_client = httpx.AsyncClient(timeout=5)
    logger.info("HTTP client создан")


@app.on_event("shutdown")
async def shutdown_event():
    await app.state.http_client.aclose()
    logger.info("HTTP client закрыт")


# ============================================================
# Upstash helper
# ============================================================

async def call_upstash(*args):
    """
    Отправляет команду в Upstash Redis через REST API.
    Использует один общий httpx.AsyncClient.
    """
    client: httpx.AsyncClient = app.state.http_client

    headers = {
        "Authorization": f"Bearer {UPSTASH_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        resp = await client.post(
            UPSTASH_URL,
            json=list(args),
            headers=headers
        )
        resp.raise_for_status()
        return resp.json().get("result")
    except httpx.RequestError as e:
        logger.error(f"❌ Ошибка Upstash: {e}")
        raise HTTPException(502, "Database connection error")


# ============================================================
# Middleware для админки
# ============================================================

@app.middleware("http")
async def admin_guard(request, call_next):
    if request.url.path.startswith("/api/admin"):
        key = request.headers.get("X-Admin-Key")
        if key != ADMIN_SECRET_KEY:
            logger.warning("⚠️ Несанкционированный доступ к /admin")
            raise HTTPException(401, "Unauthorized")
    return await call_next(request)


# ============================================================
# PUBLIC: check subscription
# ============================================================

@app.get("/check/{username}")
async def check_subscription(username: str):
    logger.info(f"Проверка подписки: {username}")

    expiry_ts = await call_upstash("HGET", f"{USER_KEY}{username}", "expiry")

    if expiry_ts is None:
        return {"active": False, "expiry": None}

    try:
        expiry_ts = float(expiry_ts)
    except ValueError:
        logger.error(f"⚠️ Некорректный expiry у {username}")
        return {"active": False, "expiry": None}

    now = datetime.utcnow().timestamp()

    if now >= expiry_ts:
        return {"active": False, "expiry": None}

    expiry_dt = datetime.utcfromtimestamp(expiry_ts)
    expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")

    return {"active": True, "expiry": expiry_str}


# ============================================================
# ADMIN: add subscription
# ============================================================

@app.post("/admin/add")
async def add_subscription(req: SubscriptionRequest):
    expiry_dt = datetime.utcnow() + timedelta(days=req.days)
    expiry_ts = int(expiry_dt.timestamp())

    # Основная запись
    await call_upstash("HSET", f"{USER_KEY}{req.username}", "expiry", expiry_ts)

    # Индекс по времени
    await call_upstash("ZADD", EXPIRY_INDEX, expiry_ts, req.username)

    expiry_str = expiry_dt.strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"✅ Выдана подписка {req.username} до {expiry_str}")

    return {
        "status": "success",
        "username": req.username,
        "days_added": req.days,
        "expiry": expiry_str
    }


# ============================================================
# ADMIN: remove subscription
# ============================================================

@app.delete("/admin/remove/{username}")
async def remove_subscription(username: str):
    await call_upstash("DEL", f"{USER_KEY}{username}")
    removed = await call_upstash("ZREM", EXPIRY_INDEX, username)

    if removed:
        logger.info(f"❌ Подписка {username} удалена")
        return {"status": "success", "message": f"{username} удалён"}
    else:
        return {"status": "not_found", "message": f"{username} не найден"}
