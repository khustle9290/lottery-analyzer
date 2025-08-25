import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import re
import os

st.title("🎲 Missouri Show Me Cash Lottery Analyzer")

# --- Sidebar Donation ---
st.sidebar.header("Support this App")
st.sidebar.markdown("[💰 Donate via PayPal](https://paypal.me/vinwills)")

# --- Instructions ---
st.markdown(
    """
**⚠️ Important:**  
The app supports both formats:  
1. Columns `Num1, Num2, ..., Num5`  
2. Column `Numbers In Order` (parsed automatically)  
Only the **first 100 rows** will be analyzed.  
Multiple separators like `-`, `–`, `—`, `,`, `:`, `;` are handled automatically.
"""
)

# --- File Upload or default ---
uploaded_file = st.file_uploader("Upload your lottery results (Excel/CSV)", type=["csv", "xlsx"])

default_file_path = r"C:\Users\vin\Downloads\ShowMeCash.xlsx"
use_default = False
if os.path.exists(default_file_path):
    use_default = st.checkbox("Use default file (ShowMeCash.xlsx)", value=False)

if uploaded_file or use_default:
    # Load only first 100 rows
    if use_default:
        df = pd.read_excel(default_file_path, nrows=100)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, nrows=100)
    else:
        df = pd.read_excel(uploaded_file, nrows=100)

    # --- Detect number columns (Num1–Num5) ---
    number_cols = [col for col in df.columns if re.match(r"Num\d+", col)]

    if number_cols:
        # Already in Num1–Num5 format
        nums_df = df[number_cols].apply(pd.to_numeric, errors='coerce')
    elif "Numbers In Order" in df.columns:
        # Parse Numbers In Order safely
        nums_df = df["Numbers In Order"].astype(str).str.split(r'\s*[-–—,:;]\s*', expand=True)
        nums_df = nums_df.applymap(lambda x: pd.to_numeric(str(x).strip(), errors='coerce'))
    else:
        st.error("No valid number columns found (Num1–Num5 or Numbers In Order).")
        st.stop()

    # Rename columns dynamically
    nums_df.columns = [f"Num{i+1}" for i in range(nums_df.shape[1])]
    number_cols = nums_df.columns.tolist()

    # Merge Draw Date if exists
    if "Draw Date" in df.columns:
        df = pd.concat([df["Draw Date"], nums_df], axis=1)
    else:
        df = nums_df

    # --- Preview Data ---
    st.subheader("Preview of First 100 Rows")
    st.dataframe(df.head(100))

    # ---------------------------
    # Sum Analysis
    # ---------------------------
    st.subheader("Sum Range Analysis & Statistical Summary")
    df["Sum"] = df[number_cols].sum(axis=1, skipna=True)

    summary_stats = {
        'Mean': df['Sum'].mean(),
        'Median': df['Sum'].median(),
        'Mode': df['Sum'].mode()[0] if not df['Sum'].mode().empty else None,
        'Min': df['Sum'].min(),
        'Max': df['Sum'].max(),
        'Range': df['Sum'].max() - df['Sum'].min(),
        'Variance': df['Sum'].var(),
        'Standard Deviation': df['Sum'].std(),
        'Q1': df['Sum'].quantile(0.25),
        'Q2 (Median)': df['Sum'].median(),
        'Q3': df['Sum'].quantile(0.75)
    }
    st.write(summary_stats)

    # Histogram
    fig, ax = plt.subplots()
    df["Sum"].plot(kind="hist", bins=20, ax=ax, edgecolor="black")
    ax.set_title("Distribution of Draw Sums")
    ax.set_xlabel("Sum Value")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # Highlight most common range (IQR)
    iqr_range = (df["Sum"].quantile(0.25), df["Sum"].quantile(0.75))
    st.write(f"✅ Most common sum range (IQR): **{int(iqr_range[0])} – {int(iqr_range[1])}**")

    # ---------------------------
    # Odd/Even per row
    # ---------------------------
    st.subheader("Odd/Even Breakdown per Row")
    def row_odd_even(row):
        odd = (row % 2 != 0).sum()
        even = (row % 2 == 0).sum()
        return f"{odd}/{even}"

    df["Odd/Even"] = df[number_cols].apply(row_odd_even, axis=1)
    st.dataframe(df[number_cols + ["Odd/Even"]])
