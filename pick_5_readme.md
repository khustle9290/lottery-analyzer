# Pick 5 Dataset Generator 🎲

Streamlined Streamlit app to generate potential Pick 5 lottery datasets based on historical data and statistical patterns.

---

## Features

- Upload historical Pick 5 data (Excel/CSV) with columns: `Num1` to `Num5`.
- Generate potential datasets considering:
  - Sum within historical mean ± standard deviation
  - Odd/even breakdown per row
  - Gaps between numbers
  - Triangular numbers count
- Display top 50 generated datasets in-app.
- Optional CSV download of results.

---

## File Format Example

| Draw Date | Num1 | Num2 | Num3 | Num4 | Num5 |
|-----------|------|------|------|------|------|
| 01-Jan-25 | 3    | 8    | 12   | 19   | 27   |
| 03-Jan-25 | 5    | 9    | 14   | 21   | 30   |

`Draw Date` is optional. Supported file types: `.xlsx` or `.csv`.

---

## Installation

```bash
pip install streamlit pandas numpy matplotlib
```

Run the app:

```bash
streamlit run app.py
```

---

## Usage

1. Open the app in your browser.
2. Upload historical Pick 5 file.
3. Click **Generate Datasets**.
4. View top 50 datasets in the table.
5. Optional: Download CSV of generated datasets.

---

## Notes

- No duplicate datasets from historical data.
- Works immediately in-app; no local Excel output required.
- Supports Pick 5 games with numbers between 1–39.

---

## Donate

Support development via PayPal: [💰 Donate](https://paypal.me/vinwills)

