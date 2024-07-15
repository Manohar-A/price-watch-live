class Price_Tracker_Config:
    MONGO_LOCAL = "mongodb://localhost:27017"
    MONGO_URL = "MONGO_URL"
    LOCALHOST = "http://localhost:8000"
    DB_NAME = "price_watch_live"
    COIN_DATA_COLLECTION = "coin_data"

    DEFAULT_ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    POLLING_INTERVAL = 10
    POLLING_URL = "POLLING_URL"
    API_KEY = "38d2b40a-67d1-4d09-9d55-fc1e487cac1a"
    API_URL = "https://api.livecoinwatch.com/coins/single"
