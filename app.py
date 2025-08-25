import pandas as pd
import itertools
import streamlit as st
import matplotlib.pyplot as plt

st.title("🎲 Missouri Show Me Cash Lottery Analyzer")

# --- Sidebar Donation ---
st.sidebar.header("Support this App")
st.sidebar.markdown("[💰 Donate via PayPal](https://paypal.me/vinwills)")

# --- User Instructions ---
st.markdown(
    """
**⚠️ Important:**  
Please make sure your uploaded file has column headings as follows:  
`Num1, Num2, Num3, Num4, Num5`  
This ensures the app reads your lottery numbers correctly.
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

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    all_numbers = df[number_cols].values.flatten()
    all_numbers_series = pd.Series(all_numbers)

    # Frequency of numbers
    freq = all_numbers_series.value_counts().sort_index()
    st.subheader("Number Frequency")
    st.bar_chart(freq)

    hot = freq.head(5)
    cold = freq.tail(5)

    st.write("🔥 Hot Numbers (most frequent):")
    st.write(hot)
    st.write("❄️ Cold Numbers (least frequent):")
    st.write(cold)

    # Pair frequency
    st.subheader("Most Common Pairs")
    pairs = []
    for row in df[number_cols].values:
        row_pairs = itertools.combinations(sorted(row), 2)
        pairs.extend(row_pairs)

    pair_series = pd.Series(pairs).value_counts().head(10)
    st.write(pair_series)

    # --- Odd/Even breakdown per row (counts only) ---
    st.subheader("Odd/Even Breakdown per Row")

    def row_odd_even_count(row):
        odd_count = (row % 2 != 0).sum()
        even_count = (row % 2 == 0).sum()
        return f"{odd_count}/{even_count}"

    df["Odd/Even"] = df[number_cols].apply(row_odd_even_count, axis=1)
    st.dataframe(df[["Odd/Even"] + number_cols])

    # --- Sum Range Analysis ---
    st.subheader("Sum Range Analysis")

    df["Sum"] = df[number_cols].sum(axis=1)

    st.write("📊 Summary Statistics for Sums:")
    st.write(df["Sum"].describe())

    # Histogram of sum values
    fig, ax = plt.subplots()
    df["Sum"].plot(kind="hist", bins=20, ax=ax, edgecolor="black")
    ax.set_title("Distribution of Draw Sums")
    ax.set_xlabel("Sum Value")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    # Highlight common range (where most sums fall)
    most_common_range = (df["Sum"].quantile(0.25), df["Sum"].quantile(0.75))
    st.write(f"✅ Most common sum range (IQR): **{int(most_common_range[0])} – {int(most_common_range[1])}**")
