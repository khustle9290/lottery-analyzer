import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import re

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

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Automatically detect number columns
    number_cols = [col for col in df.columns if "Num" in col]

    # If no Num1–Num5 columns exist, parse single column
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

        # Convert to DataFrame and ints
        nums_df = pd.DataFrame(nums_df.tolist())
        nums_df = nums_df.apply(lambda col: col.str.strip().astype(int))

        # Sort ascending
        nums_df = nums_df.apply(lambda row: sorted(row), axis=1, result_type='expand')
        nums_df.columns = [f"Num{i+1}" for i in range(nums_df.shape[1])]

        # Merge with original df
        df = pd.concat([df, nums_df], axis=1)
        number_cols = nums_df.columns.tolist()

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
        'Mode': df['Sum'].mode()[0],
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
