# run.py

import os
import pandas as pd
from scraper import scrape_all_products
from utils import setup_logging
from config import (
    CSV_LATEST, CSV_HISTORY,
    CSV_PRICE_CHANGE, CSV_NEW_RENAMED
)

setup_logging()

def compare_and_save(new_data):
    if not new_data:
        print("⚠️ No data to compare.")
        return

    new_df = pd.DataFrame(new_data)
    new_df.drop_duplicates(subset="SKU", inplace=True)

    # Save history
    if os.path.exists(CSV_HISTORY):
        history_df = pd.read_csv(CSV_HISTORY)
        history_df = pd.concat([history_df, new_df], ignore_index=True)
    else:
        history_df = new_df.copy()

    history_df.to_csv(CSV_HISTORY, index=False)
    new_df.to_csv(CSV_LATEST, index=False)

    if not os.path.exists(CSV_LATEST):
        print("🟡 First run — all products treated as new.")
        return

    old_df = pd.read_csv(CSV_LATEST)
    old_df["SKU"] = old_df["SKU"].astype(str)
    new_df["SKU"] = new_df["SKU"].astype(str)

    old_index = {row["SKU"]: row for _, row in old_df.iterrows()}
    new_index = {row["SKU"]: row for _, row in new_df.iterrows()}

    new_products = []
    renamed = []
    price_changes = []

    for sku, new_row in new_index.items():
        if sku not in old_index:
            new_products.append(new_row)
        else:
            old_row = old_index[sku]

            if new_row["Title"] != old_row["Title"]:
                renamed.append({
                    "SKU": sku,
                    "Old Title": old_row["Title"],
                    "New Title": new_row["Title"],
                    "Link": new_row["Link"]
                })

            try:
                old_price = float(old_row.get("Sale Price") or old_row.get("Regular Price"))
                new_price = float(new_row.get("Sale Price") or new_row.get("Regular Price"))
                if old_price != new_price:
                    price_changes.append({
                        "SKU": sku,
                        "Title": new_row["Title"],
                        "Old Price": old_price,
                        "New Price": new_price,
                        "Link": new_row["Link"],
                        "Date": new_row["Date"]
                    })
            except:
                continue

    if new_products or renamed:
        changes_df = pd.DataFrame(
            [dict(p, **{"Change Type": "New"}) for p in new_products] +
            [dict(p, **{"Change Type": "Renamed"}) for p in renamed]
        )
        changes_df.to_csv(CSV_NEW_RENAMED, index=False)

    if price_changes:
        pd.DataFrame(price_changes).to_csv(CSV_PRICE_CHANGE, index=False)

    print(f"✅ Summary: New={len(new_products)}, Renamed={len(renamed)}, Price Changes={len(price_changes)}")

def main():
    print("📡 Starting scrape...")
    results, errors = scrape_all_products()
    print(f"✅ Products scraped: {len(results)}")
    if errors:
        with open("errors.log", "a") as f:
            for url in errors:
                f.write(url + "\n")
        print(f"⚠️ {len(errors)} failed. Logged in errors.log.")
    compare_and_save(results)

if __name__ == "__main__":
    main()
