import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import re
import os

st.title("🎲 Missouri Show Me Cash Lottery Analyzer")

# --- Sidebar Donation ---
st.sidebar.header("Support this App")
st.sidebar.markdown("[💰 Donate via PayPal](https://paypal.me/vinwills)")

# --- User Instructions ---
st.markdown(
    """
**⚠️ Important:**  
Please make sure your uploaded file either has column headings as follows:  
`Num1, Num2, Num3, Num4, Num5`  
OR contains a column called `Numbers In Order` or `Numbers As Drawn`.  
The app will handle both formats automatically.  
Only the **first 100 rows** will be analyzed.
"""
)

# --- File Upload or default ---
uploaded_file = st.file_uploader("Upload your lottery results (Excel/CSV)", type=["csv", "xlsx"])
default_file_path = r"C:\Users\vin\Downloads\ShowMeCash.xlsx"
use_default = os.path.exists(default_file_path) and st.checkbox("Use default file (ShowMeCash.xlsx)", value=False)

if uploaded_file or use_default:
    # Load only first 100 rows
    if use_default:
        df = pd.read_excel(default_file_path, nrows=100)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, nrows=100)
    else:
        df = pd.read_excel(uploaded_file, nrows=100)

    # Automatically detect number columns
    number_cols = [col for col in df.columns if "Num" in col]

    # --- If no Num1–Num5, clean in memory ---
    if not number_cols:
        # Determine column to parse
        if "Numbers In Order" in df.columns:
            num_col = "Numbers In Order"
        elif "Numbers As Drawn" in df.columns:
            num_col = "Numbers As Drawn"
        else:
            st.error("No valid number columns found.")
            st.stop()

        # Split numbers in memory (like your working script)
        nums_df = df[num_col].astype(str).str.split('--', expand=True)
        nums_df = nums_df.applymap(lambda x: str(x).strip())

        # Rename columns
        nums_df.columns = [f"Num{i+1}" for i in range(nums_df.shape[1])]

        # Add Draw Date back in
        if "Draw Date" in df.columns:
            cleaned_df = pd.concat([df["Draw Date"], nums_df], axis=1)
        else:
            cleaned_df = nums_df

        df = cleaned_df
        number_cols = nums_df.columns.tolist()

    # --- Preview Data ---
    st.subheader("Preview of First 100 Rows")
    st.dataframe(df.head(100))

    # ---------------------------
    # Sum Analysis
    # ---------------------------
    st.subheader("Sum Range Analysis & Statistical Summary")
    df["Sum"] = df[number_cols].astype(int).sum(axis=1)

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

    # Highlight most common range
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

    df["Odd/Even"] = df[number_cols].astype(int).apply(row_odd_even, axis=1)
    st.dataframe(df[number_cols + ["Odd/Even"]])
