import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
import math

# --- Page config with custom icon ---
st.set_page_config(
    page_title="Pick 5 Patterns & Trends",
    page_icon=r"C:\Users\vin\Downloads\lottery-analyzer\balls.png",
    layout="centered"
)

# --- Title & subtitle ---
st.title("Pick 5 Patterns & Trends")
st.write("Analyze number patterns across different Pick 5 ranges (1–32, 1–36, 1–39).")

# --- Instructions ---
st.markdown(
    """
**📄 Instructions for File Upload:**  
- Your file should be in **Excel (.xlsx)** or **CSV (.csv)** format.  
- Columns must be labeled **Num1, Num2, Num3, Num4, Num5**.  
- Each row represents a single Pick 5 draw.  
- Optionally, include a **Draw Date** column in the first column.  
- The app will automatically parse the numbers, calculate the **sum**, show **odd/even breakdown**, and count **triangular numbers**.
"""
)

# --- Example table ---
st.subheader("Example of the file format")
example_data = {
    "Draw Date": ["2025-08-24", "2025-08-23", "2025-08-22"],
    "Num1": [4, 8, 8],
    "Num2": [6, 11, 9],
    "Num3": [10, 29, 13],
    "Num4": [13, 32, 15],
    "Num5": [29, 38, 29],
}
example_df = pd.DataFrame(example_data)
st.table(example_df)

# --- File uploader ---
uploaded_file = st.file_uploader("Upload your Pick 5 Excel or CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Determine file type and read
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # --- Detect usable column (Num1..Num5) ---
        number_cols = [col for col in df.columns if re.match(r"(?i)^num\d+$", col)]
        if number_cols:
            df_numbers = df[number_cols].apply(pd.to_numeric, errors="coerce")
        else:
            st.error("No valid number columns found. Please ensure your file has Num1–Num5.")
            st.stop()

        # Rename columns Num1..Num5
        df_numbers.columns = [f"Num{i}" for i in range(1, 6)]

        # Combine with Draw Date if available
        if "Draw Date" in df.columns:
            df_final = pd.concat([df["Draw Date"], df_numbers], axis=1)
        else:
            df_final = df_numbers

        # --- Compute Sum ---
        df_final["Sum"] = df_numbers.sum(axis=1, skipna=True)

        # --- Odd/Even and Triangular Number Analysis ---
        def odd_even_status(number):
            return "even" if number % 2 == 0 else "odd"

        def is_triangular_number(number):
            if number < 1:
                return False
            n = (math.sqrt(8 * number + 1) - 1) / 2
            return n.is_integer()

        odd_even_list = []
        tri_count_list = []

        for _, row in df_numbers.iterrows():
            odd = even = tri_count = 0
            for num in row:
                if pd.notna(num):
                    if num % 2 == 0:
                        even += 1
                    else:
                        odd += 1
                    if is_triangular_number(num):
                        tri_count += 1
            odd_even_list.append(f"{odd} odd / {even} even")
            tri_count_list.append(tri_count)

        df_final["Odd/Even"] = odd_even_list
        df_final["Tri Count"] = tri_count_list

        # --- Display cleaned data with odd/even and triangular info ---
        st.subheader("Cleaned Pick 5 Data with Odd/Even & Triangular Number Counts")
        st.dataframe(df_final)

        # --- Statistical Summary ---
        st.subheader("Statistical Summary of Draw Sums")
        sum_series = df_final["Sum"]

        summary_stats = {
            "Mean (Average Sum)": sum_series.mean(),
            "Median (Middle Sum)": sum_series.median(),
            "Mode (Most Common Sum)": sum_series.mode()[0] if not sum_series.mode().empty else None,
            "Minimum Sum": sum_series.min(),
            "Maximum Sum": sum_series.max(),
            "Range (Max - Min)": sum_series.max() - sum_series.min(),
            "Variance": sum_series.var(),
            "Standard Deviation": sum_series.std(),
            "Q1 (25th Percentile)": sum_series.quantile(0.25),
            "Q2 (Median)": sum_series.median(),
            "Q3 (75th Percentile)": sum_series.quantile(0.75),
        }
        st.write(summary_stats)

        # --- Histogram of sums ---
        st.subheader("Distribution of Draw Sums")
        fig, ax = plt.subplots()
        sum_series.plot(kind="hist", bins=20, edgecolor="black", ax=ax)
        ax.set_title("Histogram of Draw Sums")
        ax.set_xlabel("Sum of 5 Numbers")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)

        # --- IQR explanation ---
        iqr = (sum_series.quantile(0.25), sum_series.quantile(0.75))
        st.markdown(
            f"✅ **Most common sum range (IQR)**: {int(iqr[0])} – {int(iqr[1])}  \n"
            "This means that 50% of all draw sums fall within this range, representing the most typical totals from the draws."
        )

    except Exception as e:
        st.error(f"Error reading file: {e}")
