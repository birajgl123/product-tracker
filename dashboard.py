# dashboard.py

import pandas as pd
from config import CSV_NEW_RENAMED, CSV_PRICE_CHANGE

def print_dashboard():
    if not (os.path.exists(CSV_NEW_RENAMED) or os.path.exists(CSV_PRICE_CHANGE)):
        print("⚠️ No new or price change data found. Run the scraper first.")
        return

    if os.path.exists(CSV_NEW_RENAMED):
        df = pd.read_csv(CSV_NEW_RENAMED)

        new = df[df["Change Type"] == "New"]
        renamed = df[df["Change Type"] == "Renamed"]

        if not new.empty:
            print("\n🆕 New Products:")
            for _, row in new.iterrows():
                print(f"- {row['Title']} [{row['SKU']}]")

        if not renamed.empty:
            print("\n✏️ Renamed Products:")
            for _, row in renamed.iterrows():
                print(f"- {row['SKU']}: '{row['Old Title']}' ➜ '{row['New Title']}'")

    if os.path.exists(CSV_PRICE_CHANGE):
        df = pd.read_csv(CSV_PRICE_CHANGE)
        if not df.empty:
            print("\n💰 Price Changes:")
            for _, row in df.iterrows():
                old_price = row['Old Price']
                new_price = row['New Price']
                direction = "↑" if float(new_price) > float(old_price) else "↓"
                print(f"- {row['Title']} [{row['SKU']}] {direction} {old_price} ➜ {new_price}")

if __name__ == "__main__":
    import os
    print_dashboard()
