# utils.py

import re
import os
import logging

def normalize_price(price_str):
    if not price_str:
        return ""
    try:
        price = re.findall(r"\d+\.?\d*", price_str.replace(",", ""))
        return float(price[0]) if price else ""
    except Exception:
        return ""

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def setup_logging():
    logging.basicConfig(
        filename="errors.log",
        level=logging.ERROR,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
