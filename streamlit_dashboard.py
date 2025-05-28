# streamlit_dashboard.py

import streamlit as st
import pandas as pd
import os

from config import CSV_NEW_RENAMED, CSV_PRICE_CHANGE

st.set_page_config(page_title="Product Tracker Dashboard", layout="wide")

st.title("🛒 Product Tracker Dashboard")

# --- New / Renamed Products
if os.path.exists(CSV_NEW_RENAMED):
    st.subheader("📦 New or Renamed Products")
    df = pd.read_csv(CSV_NEW_RENAMED)

    if "Change Type" in df.columns:
        change_type = st.selectbox("Filter by change type", df["Change Type"].unique())
        filtered = df[df["Change Type"] == change_type]

        st.write(f"Total {change_type} products: {len(filtered)}")
        st.dataframe(filtered)
    else:
        st.warning("No 'Change Type' column found in new/renamed file.")
else:
    st.info("No new or renamed product data available.")

# --- Price Changes
if os.path.exists(CSV_PRICE_CHANGE):
    st.subheader("💰 Price Changes")
    price_df = pd.read_csv(CSV_PRICE_CHANGE)

    if not price_df.empty:
        st.write(f"Total price changes: {len(price_df)}")
        st.dataframe(price_df)
    else:
        st.info("No price changes found.")
else:
    st.info("Price change data not available.")

