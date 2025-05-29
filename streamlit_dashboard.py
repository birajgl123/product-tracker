import streamlit as st
import pandas as pd
import os

# File paths (adjust if needed)
CSV_LATEST = "nidhi_prices.csv"
CSV_NEW_RENAMED = "new_or_renamed_products.csv"
CSV_PRICE_CHANGE = "price_changes.csv"

st.title("🛒 Product Tracker Dashboard")

# Load latest products snapshot
if os.path.exists(CSV_LATEST):
    latest_df = pd.read_csv(CSV_LATEST)
else:
    st.error(f"Latest data file not found: {CSV_LATEST}")
    st.stop()

# Load new/renamed data
if os.path.exists(CSV_NEW_RENAMED):
    new_renamed_df = pd.read_csv(CSV_NEW_RENAMED)
else:
    new_renamed_df = pd.DataFrame()

# Load price changes data
if os.path.exists(CSV_PRICE_CHANGE):
    price_changes_df = pd.read_csv(CSV_PRICE_CHANGE)
else:
    price_changes_df = pd.DataFrame()

# Show totals on top
st.markdown(f"### Total products tracked: **{len(latest_df)}**")
st.markdown(f"New or Renamed products: **{len(new_renamed_df)}**")
st.markdown(f"Price changes recorded: **{len(price_changes_df)}**")

# Determine price column dynamically for display
price_col_candidates = ["Price", "Price_raw", "Sale Price", "Regular Price"]
price_col = None
for col in price_col_candidates:
    if col in latest_df.columns:
        price_col = col
        break

if price_col is None:
    st.warning(f"No recognized price column found in latest data. Columns available: {latest_df.columns.tolist()}")
else:
    # Display latest products table (limited to 50 rows for performance)
    display_df = latest_df[["Title", "SKU", price_col, "Link"]].copy()
    display_df = display_df.rename(columns={price_col: "Price"})
    st.markdown("### Latest Products Snapshot")
    st.dataframe(display_df.head(50))

# Show New/Renamed Products details
if not new_renamed_df.empty:
    st.markdown("### New / Renamed Products")
    if "Change Type" not in new_renamed_df.columns:
        new_renamed_df["Change Type"] = "New / Renamed"
    st.dataframe(new_renamed_df.head(50))
else:
    st.info("No new or renamed product data available.")

# Show Price Changes details
if not price_changes_df.empty:
    st.markdown("### Price Changes")
    st.dataframe(price_changes_df.head(50))
else:
    st.info("Price change data not available.")
