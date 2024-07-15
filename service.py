import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import Price_Tracker_Config
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models import CoinDataDocument
import httpx


_mongo_client = None


def get_mongo_client():
    global _mongo_client
    if _mongo_client is None:
        conn_str = os.environ.get(
            Price_Tracker_Config.MONGO_URL, Price_Tracker_Config.MONGO_LOCAL
        )
        _mongo_client = AsyncIOMotorClient(conn_str, tz_aware=True)
    return _mongo_client


def get_curr_time():
    return datetime.now(timezone.utc)


async def get_price_data(coin_code: str, currency: str):
    async with httpx.AsyncClient() as client:
        url = Price_Tracker_Config.API_URL
        payload = {"currency": currency, "code": coin_code}
        headers = {
            "x-api-key": Price_Tracker_Config.API_KEY,
        }
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )


async def fetch_and_store_coin_data(code, currency):
    print(f"Fetching data for {code}")
    try:
        data = await get_price_data(code, currency)
        current_time = get_curr_time()
        coin_data = CoinDataDocument(
            **data, code=code, currency=currency, created_at=current_time
        )
        await CoinDataDocument.insert_one(coin_data)
    except Exception as e:
        print(f"Error fetching data for {code}: {str(e)}")

    print(f"Data fetched and stored for {code}")
