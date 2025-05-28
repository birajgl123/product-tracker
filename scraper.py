import json
import logging
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import OrderedDict

import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm

from config import MAIN_SITEMAP_URL, HEADERS, MAX_WORKERS, REQUEST_RETRIES, REQUEST_TIMEOUT
from utils import normalize_price

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scraper = cloudscraper.create_scraper()

def fetch_with_retries(url, retries=REQUEST_RETRIES, timeout=REQUEST_TIMEOUT):
    wait = 5
    for attempt in range(1, retries + 1):
        try:
            response = scraper.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except Exception as e:
            if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                logging.warning(f"429 Too Many Requests for {url}, sleeping {wait} seconds (attempt {attempt})")
                time.sleep(wait)
                wait *= 2  # exponential backoff
            else:
                logging.warning(f"Error fetching {url} (attempt {attempt}): {e}")
                time.sleep(wait)
    return None

def load_soup(url, parser="html.parser"):
    response = fetch_with_retries(url)
    if response:
        return BeautifulSoup(response.content, parser)
    return None

def get_sitemap_urls():
    soup = load_soup(MAIN_SITEMAP_URL, parser="xml")
    if not soup:
        logging.error("Failed to load master sitemap.")
        return []
    return [loc.text for loc in soup.find_all("loc") if "sitemap_products" in loc.text]

def get_product_urls(sitemap_urls):
    product_urls = []
    for sitemap_url in sitemap_urls:
        soup = load_soup(sitemap_url, parser="xml")
        if not soup:
            logging.warning(f"Failed to load sitemap: {sitemap_url}")
            continue
        urls = [loc.text for loc in soup.find_all("loc") if "/products/" in loc.text]
        product_urls.extend(urls)
    return list(OrderedDict.fromkeys(product_urls))

def scrape_product(url):
    soup = load_soup(url)
    if not soup:
        logging.error(f"Failed to scrape {url}")
        return None

    try:
        title = next((tag.text.strip() for tag in [
            soup.select_one("h1.product-title"),
            soup.select_one("h1.product__title"),
            soup.select_one("h1.h2"),
            soup.select_one("h1")
        ] if tag), "No title found")

        sale_tag = soup.select_one("span.price-item--sale, span.sale-price")
        regular_tag = soup.select_one("span.price-item--regular, span.regular-price")

        sale_price = sale_tag.text.strip() if sale_tag else ""
        regular_price = regular_tag.text.strip() if regular_tag else sale_price

        sku = None
        for sel in ["span.sku", "span.product-sku", "span.variant-sku", "div.sku", '[class*="sku"]']:
            el = soup.select_one(sel)
            if el and el.text.strip():
                sku = el.text.strip()
                break

        if not sku:
            ld_json = soup.find("script", type="application/ld+json")
            if ld_json:
                try:
                    data = json.loads(ld_json.string)
                    if isinstance(data, dict) and "sku" in data:
                        sku = data["sku"]
                    elif isinstance(data, list):
                        for entry in data:
                            if isinstance(entry, dict) and "sku" in entry:
                                sku = entry["sku"]
                                break
                except Exception:
                    pass

        if not sku:
            sku = "No SKU found"

        # Delay to avoid rate limiting
        time.sleep(random.uniform(3, 6))

        return {
            "Title": title,
            "Sale Price": normalize_price(sale_price),
            "Regular Price": normalize_price(regular_price),
            "SKU": sku,
            "Link": url,
            "Date": datetime.today().strftime("%Y-%m-%d")
        }

    except Exception as e:
        logging.error(f"Failed to parse {url}: {e}")
        return None

def scrape_all_products():
    sitemap_urls = get_sitemap_urls()
    if not sitemap_urls:
        logging.error("No product sitemaps found.")
        return [], []

    product_urls = get_product_urls(sitemap_urls)
    if not product_urls:
        logging.error("No product URLs found.")
        return [], []

    logging.info(f"Total products to scrape: {len(product_urls)}")

    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(scrape_product, url): url for url in product_urls}
        for i, future in enumerate(tqdm(as_completed(future_to_url), total=len(product_urls), desc="Scraping Products"), 1):
            url = future_to_url[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
                else:
                    errors.append(url)
            except Exception as e:
                logging.error(f"Unhandled error scraping {url}: {e}")
                errors.append(url)
            logging.info(f"Scraped {i}/{len(product_urls)} products")

    logging.info(f"Scraping complete: {len(results)} success, {len(errors)} failed")
    return results, errors

if __name__ == "__main__":
    results, errors = scrape_all_products()
    print(f"Scraped {len(results)} products successfully. Failed: {len(errors)}")
