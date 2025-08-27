import streamlit as st
import pandas as pd
import re

# --- Page config with custom icon ---
st.set_page_config(
    page_title="Pick 5 Patterns & Trends",
    page_icon=r"C:\Users\vin\Downloads\lottery-analyzer\balls.png",
    layout="centered"
)

# --- Title & subtitle ---
st.title("Pick 5 Patterns & Trends")
st.write("Analyze number patterns across different Pick 5 ranges (1–32, 1–36, 1–39).")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload your Pick 5 Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file)

        # --- Detect usable column (prefer "Numbers In Order") ---
        usable_col = None
        for col in df.columns:
            if "Numbers In Order" in col:
                usable_col = col
                break
        # Fallback to 4th column if "Numbers In Order" not found
        if usable_col is None and len(df.columns) > 3:
            usable_col = df.columns[3]

        if usable_col is None:
            st.error("Could not find 'Numbers In Order' column or a valid fallback column.")
        else:
            # --- Parse numbers robustly ---
            df[usable_col] = df[usable_col].astype(str).apply(
                lambda x: re.split(r"\s*[-–—,:;]\s*|\s+", x.strip())
            )

            # Expand into separate columns
            df_numbers = pd.DataFrame(df[usable_col].tolist())
            df_numbers = df_numbers.apply(pd.to_numeric, errors="coerce")

            # Rename columns Num1..Num5
            df_numbers = df_numbers.iloc[:, :5]  # keep only first 5 numbers
            df_numbers = df_numbers.reindex(columns=range(5))  # pad if fewer than 5
            df_numbers.columns = [f"Num{i}" for i in range(1, 6)]

            # Combine with Draw Date if available
            if "Draw Date" in df.columns:
                df_final = pd.concat([df["Draw Date"], df_numbers], axis=1)
            else:
                df_final = df_numbers

            # --- Compute Sum ---
            df_final["Sum"] = df_numbers.sum(axis=1, skipna=True)

            # --- Compute Odd/Even ---
            def row_odd_even(row):
                vals = row.dropna()
                odd = (vals % 2 != 0).sum()
                even = (vals % 2 == 0).sum()
                return f"{odd}/{even}"

            df_final["Odd/Even"] = df_numbers.apply(row_odd_even, axis=1)

            # --- Display cleaned data ---
            st.subheader("Cleaned Pick 5 Data")
            st.dataframe(df_final)

    except Exception as e:
        st.error(f"Error reading file: {e}")
