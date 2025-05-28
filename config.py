# config.py

MAIN_SITEMAP_URL = "https://nidhiratna.com/sitemap.xml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                  " Chrome/114.0.0.0 Safari/537.36"
}

MAX_WORKERS = 5  # Reduced concurrency to avoid rate limit

REQUEST_RETRIES = 5
REQUEST_TIMEOUT = 15

CSV_LATEST = "nidhi_prices.csv"
CSV_HISTORY = "price_history.csv"
CSV_NEW_RENAMED = "new_or_renamed_products.csv"
CSV_PRICE_CHANGE = "price_changes.csv"
