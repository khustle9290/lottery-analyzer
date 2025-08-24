import pandas as pd
import itertools
import streamlit as st
import matplotlib.pyplot as plt

st.title("🎲 Lottery Pair & Trend Analyzer")

uploaded_file = st.file_uploader("Upload your lottery results (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    number_cols = [col for col in df.columns if "Num" in col]

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    all_numbers = df[number_cols].values.flatten()
    all_numbers = pd.Series(all_numbers)

    # Frequency of numbers
    freq = all_numbers.value_counts().sort_index()
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

    # Gap analysis
    st.subheader("Gap Analysis (Draws Since Last Appearance)")
    last_seen = {}
    for num in range(all_numbers.min(), all_numbers.max() + 1):
        try:
            last_draw = df.loc[(df[number_cols] == num).any(axis=1), "Draw Date"].iloc[-1]
            gap = df["Draw Date"].max() - last_draw
            last_seen[num] = gap.days
        except:
            last_seen[num] = None

    gap_df = pd.DataFrame.from_dict(last_seen, orient="index", columns=["Days Since Last Seen"])
    st.dataframe(gap_df.sort_values("Days Since Last Seen", ascending=False).head(10))

    st.markdown("---")
    st.markdown("☕ Like this tool? [Buy me a coffee](https://www.buymeacoffee.com/yourusername)")
