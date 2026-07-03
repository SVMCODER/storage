"""
Preliminary Data Analysis & Data Quality Assessment
----------------------------------------------------
Feasibility check for: "What Drives Customer Churn Among High-Value Online
Retail Customers? An Explainable Machine Learning Approach"

NOTE ON DATA: The target dataset is the UCI "Online Retail" transactional
dataset (Chen, Sain & Guo, 2012; UCI ML Repository, DOI: 10.24432/C5BW33),
541,909 invoice-line transactions for a UK-based online gift retailer
between 01/12/2010 and 09/12/2011. Direct file download was not available
from this offline analysis environment, so a structurally faithful sample
(same 8 columns, same data-quality issues, same approximate proportions
reported for the real file: ~25% missing CustomerID, ~1.7% cancellations,
UK-dominant country mix) is generated below to validate that the planned
cleaning, RFM, and modelling pipeline runs correctly end-to-end on data of
this shape. All summary statistics for the REAL dataset reported in the
proposal text are drawn from the published dataset documentation and the
introductory paper, not from this synthetic sample.

This script produces:
  1. A data quality assessment (missing values, duplicates, cancellations,
     negative/zero prices, data types).
  2. A preliminary data analysis (summary statistics, basic cleaning,
     RFM table construction).
  3. Figure 1 (three-panel chart: missing values, order-value distribution,
     monthly transaction volume), saved as prelim_analysis_figure_v2.png.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# 0. GENERATE STRUCTURALLY FAITHFUL SAMPLE
# ---------------------------------------------------------------
rng = np.random.default_rng(42)
N = 6000  # illustrative sample size (real file has 541,909 rows)

countries = (["United Kingdom"] * 91 + ["Germany"] * 3 + ["France"] * 2 +
             ["Eire"] * 2 + ["Spain"] * 1 + ["Netherlands"] * 1)
dates = pd.date_range("2010-12-01", "2011-12-09", freq="min")

n_cancel = int(N * 0.017)
n_normal = N - n_cancel

invoice_no = [str(536365 + i) for i in range(n_normal)] + \
             ["C" + str(540000 + i) for i in range(n_cancel)]
quantity = list(rng.integers(1, 40, n_normal)) + list(-rng.integers(1, 20, n_cancel))
unit_price = np.round(rng.gamma(2.0, 2.5, N), 2)
unit_price[rng.choice(N, size=int(N * 0.001), replace=False)] = 0.0  # data-entry errors

customer_id = rng.integers(12346, 18287, N).astype(float)
missing_idx = rng.choice(N, size=int(N * 0.25), replace=False)
customer_id[missing_idx] = np.nan

df = pd.DataFrame({
    "InvoiceNo": invoice_no,
    "StockCode": rng.integers(10000, 99999, N).astype(str),
    "Description": rng.choice(
        ["WHITE HANGING HEART", "REGENCY TEA SET", "VINTAGE MUG",
         "PARTY BUNTING", "RETRO TIN SIGN", "GLASS CANDLE HOLDER"], N),
    "Quantity": quantity,
    "InvoiceDate": rng.choice(dates, N),
    "UnitPrice": unit_price,
    "CustomerID": customer_id,
    "Country": rng.choice(countries, N),
})
df["OrderValue"] = df["Quantity"] * df["UnitPrice"]

# ---------------------------------------------------------------
# 1. DATA QUALITY ASSESSMENT
# ---------------------------------------------------------------
print("=" * 60)
print("DATA QUALITY ASSESSMENT (illustrative sample, n =", N, ")")
print("=" * 60)

missing = df.isna().sum()
missing_pct = (missing / len(df) * 100).round(1)
quality_report = pd.DataFrame({"missing_count": missing, "missing_pct": missing_pct})
print("\nMissing values by column:\n", quality_report[quality_report.missing_count > 0])

n_dupes = df.duplicated().sum()
print("\nExact duplicate rows:", n_dupes)

n_cancellations = df["InvoiceNo"].str.startswith("C").sum()
print("Cancelled transactions (InvoiceNo starts with 'C'):", n_cancellations,
      f"({n_cancellations/len(df)*100:.1f}% )")

n_neg_qty = (df["Quantity"] < 0).sum()
n_zero_price = (df["UnitPrice"] == 0).sum()
print("Negative-quantity rows:", n_neg_qty)
print("Zero-price rows (likely data-entry errors):", n_zero_price)

print("\nColumn data types:\n", df.dtypes)

# ---------------------------------------------------------------
# 2. PRELIMINARY DATA ANALYSIS
# ---------------------------------------------------------------
print("\n" + "=" * 60)
print("PRELIMINARY DATA ANALYSIS")
print("=" * 60)

print("\nSummary statistics (Quantity, UnitPrice, OrderValue):")
print(df[["Quantity", "UnitPrice", "OrderValue"]].describe().round(2))

clean = df[(df.Quantity > 0) & (df.UnitPrice > 0) & df.CustomerID.notna()].copy()
print(f"\nRows retained after basic cleaning rules: {len(clean)} of {len(df)} "
      f"({len(clean)/len(df)*100:.1f}%)")

rfm = clean.groupby("CustomerID").agg(
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("OrderValue", "sum"),
    LastPurchase=("InvoiceDate", "max"),
).reset_index()
snapshot = clean["InvoiceDate"].max() + pd.Timedelta(days=1)
rfm["Recency"] = (snapshot - rfm["LastPurchase"]).dt.days
print("\nRFM table preview (first 5 customers):")
print(rfm[["CustomerID", "Recency", "Frequency", "Monetary"]].head())

# ---------------------------------------------------------------
# 3. FIGURE 1: DATA QUALITY & PRELIMINARY ANALYSIS OVERVIEW
# ---------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))

quality_report[quality_report.missing_count > 0]["missing_pct"].plot(
    kind="bar", ax=axes[0], color="#C00000")
axes[0].set_title("Missing Values by Column (%)", fontsize=10)
axes[0].set_ylabel("% missing")
axes[0].tick_params(axis='x', rotation=30)

axes[1].hist(clean["OrderValue"].clip(upper=clean["OrderValue"].quantile(0.95)),
             bins=30, color="#2E75B6", edgecolor="white")
axes[1].set_title("Distribution of Order Value\n(clipped at 95th percentile)", fontsize=10)
axes[1].set_xlabel("Order value (GBP)")

monthly = clean.set_index("InvoiceDate").resample("ME").size()
axes[2].plot(monthly.index, monthly.values, marker="o", color="#548235")
axes[2].set_title("Transactions per Month (sample)", fontsize=10)
axes[2].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig("prelim_analysis_figure_v2.png", dpi=220, bbox_inches="tight")
print("\nSaved: prelim_analysis_figure_v2.png")
