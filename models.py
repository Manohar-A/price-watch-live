from beanie import Document
from datetime import datetime
from app.config import Price_Tracker_Config
import pymongo
from pymongo import IndexModel
from pydantic import Field, BaseModel
from typing import Optional, Literal


class CoinDataDocument(Document):
    code: str = Field(description="The code of the coin")
    currency: str = Field(description="The currency of the coin")
    rate: float = Field(description="The price of the coin in given currency")
    volume: float = Field(
        description="Reported trading volume of the coin in last 24 hours in given currency"
    )
    cap: float = Field(description="The market cap of the coin in given currency")
    liquidity: float = Field(description="The liquidity of the coin in given currency")
    delta: dict = Field(description="The delta of the coin")
    created_at: datetime = Field(description="The time at which the data is collected")

    class Settings:
        name = Price_Tracker_Config.COIN_DATA_COLLECTION
        indexes = [
            IndexModel(
                [("code", pymongo.ASCENDING)],
                name="code_index",
            ),
            IndexModel(
                [("created_at", pymongo.DESCENDING)],
                name="created_at_index",
            ),
        ]


class CoinDataSearchQueryParams(BaseModel):
    code: Optional[str] = None
    order: Literal["asc", "desc"] = "desc"
    sort_by: Literal["created_at"] = "created_at"
    limit: int = Price_Tracker_Config.DEFAULT_ITEMS_PER_PAGE
    offset: int = 0

    def get_search_filter(self):
        search_filter = {}
        if self.code:
            search_filter["code"] = self.code
        return search_filter


class CoinDataSearchResult(BaseModel):
    data: list[CoinDataDocument]
    total_count: int


COIN_CODES = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "solana": "SOL",
    "usd_coin": "USDC",
}
