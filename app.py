import streamlit as st
import pandas as pd
import numpy as np
import itertools
import random
import math
from io import StringIO

# --- Page config ---
st.set_page_config(
    page_title="Pick 5 Dataset Generator",
    page_icon=r"C:\Users\vin\Downloads\lottery-analyzer\balls.png",
    layout="centered"
)

st.title("Pick 5 Dataset Generator")
st.write("Generate potential Pick 5 datasets based on historical patterns and constraints.")

# --- Instructions ---
st.markdown("""
**Instructions:**  
- Upload historical Pick 5 data (Excel/CSV) with columns: `Num1, Num2, Num3, Num4, Num5`.  
- Optionally include a `Draw Date` column.  
- Click **Generate Datasets** to see potential new combinations.
""")

st.subheader("📄 Example of Uploaded File Format")
st.markdown(
    """
The uploaded file should be either an Excel or CSV file with **columns labeled `Num1` to `Num5`**, and optionally `Draw Date`.  

| Draw Date | Num1 | Num2 | Num3 | Num4 | Num5 |
|-----------|------|------|------|------|------|
| 25-Aug-25 | 19   | 24   | 27   | 33   | 35   |
| 24-Aug-25 | 4    | 6    | 10   | 13   | 29   |
| 23-Aug-25 | 8    | 11   | 29   | 32   | 38   |
"""
)


# --- File uploader ---
uploaded_file = st.file_uploader("Upload your historical Pick 5 data", type=["xlsx", "csv"])

# --- Function definitions ---
def is_triangular(n):
    if n < 1:
        return False
    x = (-1 + math.sqrt(1 + 8 * n)) / 2
    return x.is_integer()

def odd_even_breakdown(dataset):
    odds = sum(1 for x in dataset if x % 2 != 0)
    evens = len(dataset) - odds
    return f"{odds} odd, {evens} even"

def calculate_gaps(dataset):
    return [dataset[i+1] - dataset[i] for i in range(len(dataset)-1)]

def sum_rule(dataset_sum, mean, std_dev):
    return (mean - std_dev) <= dataset_sum <= (mean + std_dev)

def avoid_last_digit_repetition(dataset):
    last_digits = [num % 10 for num in dataset]
    return len(set(last_digits)) == len(last_digits)

def count_triangular(dataset):
    return sum(1 for num in dataset if is_triangular(num))

def generate_potential_datasets(n, past_combos, mean, std_dev):
    potential_datasets = []
    past_set = set(tuple(sorted(c)) for c in past_combos)
    previous_row_numbers = set()
    attempts = 0
    max_attempts = 20000

    while len(potential_datasets) < n and attempts < max_attempts:
        dataset = sorted(random.sample(range(1, 40), 5))
        dataset_sum = sum(dataset)

        if (tuple(dataset) not in past_set and
            sum_rule(dataset_sum, mean, std_dev) and
            avoid_last_digit_repetition(dataset) and
            previous_row_numbers.isdisjoint(dataset)):
            
            potential_datasets.append(dataset)
            previous_row_numbers = set(dataset)

        attempts += 1

    return potential_datasets

# --- Main logic ---
if uploaded_file is not None:
    try:
        # Load file
        if uploaded_file.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Ensure 5 number columns
        number_cols = [col for col in df.columns if col.lower().startswith("num")]
        if len(number_cols) != 5:
            st.error("File must have exactly 5 columns: Num1–Num5.")
            st.stop()

        df_numbers = df[number_cols].apply(pd.to_numeric, errors="coerce")
        past_combos = [list(row) for row in df_numbers.values]

        # Calculate mean and std deviation of sums
        sums = [sum(c) for c in past_combos]
        mean = np.mean(sums)
        std_dev = np.std(sums)
        st.write(f"Historical mean sum: {mean:.2f}, Std Dev: {std_dev:.2f}")

        # Generate datasets on button click
        if st.button("Generate Datasets"):
            generated = generate_potential_datasets(1000, past_combos, mean, std_dev)
            output = []
            for dataset in generated[:50]:  # show top 50
                output.append({
                    "Num1": dataset[0],
                    "Num2": dataset[1],
                    "Num3": dataset[2],
                    "Num4": dataset[3],
                    "Num5": dataset[4],
                    "Sum": sum(dataset),
                    "Odd/Even": odd_even_breakdown(dataset),
                    "Gaps": calculate_gaps(dataset),
                    "Tri Count": count_triangular(dataset)
                })

            output_df = pd.DataFrame(output)
            st.subheader("Top Generated Datasets")
            st.dataframe(output_df)

            # --- Optional CSV download ---
            csv = output_df.to_csv(index=False)
            st.download_button(
                label="Download Generated Datasets as CSV",
                data=csv,
                file_name="generated_pick5.csv",
                mime="text/csv"
            )

    except Exception as e:
        st.error(f"Error processing file: {e}")
