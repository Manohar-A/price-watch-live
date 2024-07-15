from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from app.config import Price_Tracker_Config
from beanie import init_beanie
from app.models import (
    CoinDataDocument,
    CoinDataSearchQueryParams,
    CoinDataSearchResult,
    COIN_CODES,
)
from app.service import get_mongo_client, fetch_and_store_coin_data
import asyncio

jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    print("Polling started")

    db_client = get_mongo_client()
    await init_beanie(
        database=db_client[Price_Tracker_Config.DB_NAME],
        document_models=[CoinDataDocument],
    )
    yield
    print("Polling stopped")
    scheduler.shutdown()
    db_client.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def hello():
    return {"Hello": "Welcome to Price Watch Live API!"}


@scheduler.scheduled_job("interval", seconds=Price_Tracker_Config.POLLING_INTERVAL)
async def poll_url():
    semaphore = asyncio.Semaphore(5)  # Limiting concurrent requests to 5
    print("Data collection started")
    currency = "USD"
    tasks = [fetch_and_store_coin_data(code, currency) for code in COIN_CODES.values()]
    await asyncio.gather(*tasks, return_exceptions=True)
    print("Data collection completed")


@app.get(
    "/coin-data",
    summary="Search for coin data",
    response_model=CoinDataSearchResult,
)
async def get_coin_data(
    search_params: CoinDataSearchQueryParams = Depends(CoinDataSearchQueryParams),
):
    search_filter = search_params.get_search_filter()
    sort_prefix = "-" if search_params.order == "desc" else ""
    sort_by = sort_prefix + search_params.sort_by

    coin_data_list = (
        await CoinDataDocument.find(search_filter)
        .skip(search_params.offset)
        .limit(search_params.limit)
        .sort(sort_by)
        .to_list(search_params.limit)
    )
    total_count = await CoinDataDocument.find(search_filter).count()
    return CoinDataSearchResult(data=coin_data_list, total_count=total_count)
