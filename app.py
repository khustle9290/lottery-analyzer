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
"""
)

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your lottery results (Excel/CSV)", type=["csv", "xlsx"])

# --- Optional: Automatically use cleaned default file ---
default_file_path = r"C:\Users\vin\Downloads\SMC\updatedSMC.xlsx"
use_default = False
if os.path.exists(default_file_path):
    use_default = st.checkbox("Use default cleaned file (updatedSMC.xlsx)", value=False)

if uploaded_file or use_default:
    # Load file
    if use_default:
        df = pd.read_excel(default_file_path)
    elif uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Automatically detect number columns
    number_cols = [col for col in df.columns if "Num" in col]

    # --- If no Num1–Num5 columns exist, parse single column ---
    if not number_cols:
        if "Numbers In Order" in df.columns:
            num_col = "Numbers In Order"
        elif "Numbers As Drawn" in df.columns:
            num_col = "Numbers As Drawn"
        else:
            st.error("No valid number columns found.")
            st.stop()

        # Split numbers using regex for multiple separators
        nums_df = df[num_col].astype(str).apply(
            lambda x: re.split(r"\s*[-–—,:;]\s*|\s{2,}", x.strip())
        )

        # Convert list of numbers into DataFrame
        nums_df = pd.DataFrame(nums_df.tolist())

        # Clean spaces & filter only digits before converting to int
        nums_df = nums_df.applymap(lambda val: int(val.strip()) if isinstance(val, str) and val.strip().isdigit() else None)

        # Drop any all-NaN rows (just in case)
        nums_df = nums_df.dropna(how="all")

        # Sort each row ascending
        nums_df = nums_df.apply(lambda row: sorted([n for n in row if pd.notna(n)]), axis=1, result_type="expand")

        # Rename columns
        nums_df.columns = [f"Num{i+1}" for i in range(nums_df.shape[1])]

        # Merge with original df
        df = pd.concat([df, nums_df], axis=1)
        number_cols = nums_df.columns.tolist()

    # --- Preview Uploaded Data ---
    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # ---------------------------
    # Statistical Analysis / Sum Range
    # ---------------------------
    st.subheader("Sum Range Analysis & Statistical Summary")
    df["Sum"] = df[number_cols].sum(axis=1)

    # Summary statistics
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

    # Histogram of sum values
    fig, ax = plt.subplots()
    df["Sum"].plot(kind="hist", bins=20, ax=ax, edgecolor="black")
    ax.set_title("Distribution of Draw Sums")
    ax.set_xlabel("Sum Value")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # Highlight most common range (IQR)
    most_common_range = (df["Sum"].quantile(0.25), df["Sum"].quantile(0.75))
    st.write(f"✅ Most common sum range (IQR): **{int(most_common_range[0])} – {int(most_common_range[1])}**")

    # ---------------------------
    # Odd/Even breakdown per row
    # ---------------------------
    st.subheader("Odd/Even Breakdown per Row")

    def row_odd_even_count(row):
        odd_count = (row % 2 != 0).sum()
        even_count = (row % 2 == 0).sum()
        return f"{odd_count}/{even_count}"

    df["Odd/Even"] = df[number_cols].apply(row_odd_even_count, axis=1)

    # Show numbers with Odd/Even last
    st.dataframe(df[number_cols + ["Odd/Even"]])
