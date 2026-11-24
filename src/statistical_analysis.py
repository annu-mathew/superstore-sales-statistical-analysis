"""
Superstore Sales Statistical Analysis
Data Analysis with Python – Internship Task 3

Run from any working directory:
    python statistical_analysis.py

Expected project structure:
Task 3/
    datasets/superstore_sales.csv
    charts/
    reports/
    screenshots/
    src/statistical_analysis.py
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import binom, poisson

warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid")

# ---------------------------------------------------------
# 1. PROJECT PATHS AND DATA LOADING
# ---------------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "datasets" / "superstore_sales.csv"

CHARTS_DIR = PROJECT_DIR / "charts"
REPORTS_DIR = PROJECT_DIR / "reports"
SCREENSHOTS_DIR = PROJECT_DIR / "screenshots"

for folder in [CHARTS_DIR, REPORTS_DIR, SCREENSHOTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}\n"
        "Please check that superstore_sales.csv is inside the datasets folder."
    )

df = pd.read_csv(DATA_PATH)

required_columns = [
    "Order Date", "Region", "Category", "Sub-Category",
    "Segment", "Sales", "Profit", "Quantity"
]
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["Month"] = df["Order Date"].dt.month
df["Year"] = df["Order Date"].dt.year
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Dataset is missing required columns: {missing_columns}")

print("\nDATASET OVERVIEW")
print("----------------")
print("Dataset shape:", df.shape)
print("Total sales records:", len(df))
print("\nFirst five records:")
print(df.head())
print("\nMissing values:")
print(df.isnull().sum())

# Convert numeric analysis columns safely.
for col in ["Sales", "Profit", "Quantity"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Sales", "Profit", "Quantity"]).copy()

# ---------------------------------------------------------
# 2. DESCRIPTIVE STATISTICS
# ---------------------------------------------------------

sales = df["Sales"]

descriptive_summary = pd.DataFrame({
    "Measure": [
        "Mean", "Median", "Mode", "Minimum", "Maximum",
        "Range", "Variance", "Standard Deviation",
        "25th Percentile (Q1)", "50th Percentile (Q2)",
        "75th Percentile (Q3)", "Interquartile Range (IQR)"
    ],
    "Value": [
        sales.mean(),
        sales.median(),
        sales.mode().iloc[0],
        sales.min(),
        sales.max(),
        sales.max() - sales.min(),
        sales.var(),
        sales.std(),
        sales.quantile(0.25),
        sales.quantile(0.50),
        sales.quantile(0.75),
        sales.quantile(0.75) - sales.quantile(0.25)
    ]
})

print("\nDESCRIPTIVE STATISTICS")
print("---------------------")
print(descriptive_summary.to_string(index=False))
descriptive_summary.to_csv(REPORTS_DIR / "descriptive_statistics.csv", index=False)

plt.figure(figsize=(10, 5))
sns.histplot(sales, bins=30, kde=True)
plt.title("Distribution of Sales")
plt.xlabel("Sales")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "sales_histogram.png", dpi=150)
plt.close()

plt.figure(figsize=(10, 4))
sns.boxplot(x=sales)
plt.title("Sales Distribution and Outliers")
plt.xlabel("Sales")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "sales_boxplot.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 3. PROBABILITY FUNDAMENTALS
# ---------------------------------------------------------

total_records = len(df)
profitable_records = int((df["Profit"] > 0).sum())
probability_profit = profitable_records / total_records

east_df = df[df["Region"] == "East"]
east_profitable = east_df[east_df["Profit"] > 0]
conditional_probability_east = (
    len(east_profitable) / len(east_df) if len(east_df) else np.nan
)

probability_east = (df["Region"] == "East").mean()
probability_profitable = (df["Profit"] > 0).mean()
probability_east_and_profitable = (
    ((df["Region"] == "East") & (df["Profit"] > 0)).mean()
)

expected_profit = df["Profit"].mean()

print("\nPROBABILITY ANALYSIS")
print("--------------------")
print(f"Probability of a profitable record: {probability_profit:.4f}")
print(f"Probability of profit in East region: {conditional_probability_east:.4f}")
print(f"P(East): {probability_east:.4f}")
print(f"P(Profitable): {probability_profitable:.4f}")
print(f"P(East) x P(Profitable): {probability_east * probability_profitable:.4f}")
print(f"P(East and Profitable): {probability_east_and_profitable:.4f}")
print(f"Expected profit per record (mean): {expected_profit:.2f}")

# ---------------------------------------------------------
# 4. PROBABILITY DISTRIBUTIONS
# ---------------------------------------------------------

sales_mean = sales.mean()
sales_std = sales.std()

x_normal = np.linspace(sales.min(), sales.max(), 1000)
normal_density = stats.norm.pdf(x_normal, loc=sales_mean, scale=sales_std)

plt.figure(figsize=(10, 5))
sns.histplot(sales, bins=40, stat="density", color="skyblue",
             label="Actual Sales Distribution")
plt.plot(x_normal, normal_density, label="Fitted Normal Curve")
plt.title("Sales Distribution with Normal Curve")
plt.xlabel("Sales")
plt.ylabel("Density")
plt.legend()
plt.tight_layout()
plt.savefig(CHARTS_DIR / "normal_distribution_sales.png", dpi=150)
plt.close()

np.random.seed(42)
uniform_data = np.random.uniform(low=10, high=100, size=1000)

plt.figure(figsize=(10, 5))
sns.histplot(uniform_data, bins=20)
plt.title("Uniform Distribution (Simulated)")
plt.xlabel("Value")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "uniform_distribution.png", dpi=150)
plt.close()

n_trials = 10
success_probability = probability_profit
successes = np.arange(0, n_trials + 1)
binomial_probabilities = binom.pmf(successes, n_trials, success_probability)

plt.figure(figsize=(10, 5))
plt.bar(successes, binomial_probabilities)
plt.title("Binomial Distribution of Profitable Records")
plt.xlabel("Number of Profitable Records")
plt.ylabel("Probability")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "binomial_distribution.png", dpi=150)
plt.close()

poisson_lambda = 5  # Illustrative rate used in the notebook
event_counts = np.arange(0, 16)
poisson_probabilities = poisson.pmf(event_counts, poisson_lambda)

plt.figure(figsize=(10, 5))
plt.bar(event_counts, poisson_probabilities)
plt.title("Poisson Distribution (Illustrative Lambda = 5)")
plt.xlabel("Number of Events")
plt.ylabel("Probability")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "poisson_distribution.png", dpi=150)
plt.close()

print("\nDISTRIBUTION EXAMPLES")
print("--------------------")
print(f"Binomial probability of exactly 8 successes in 10 trials: "
      f"{binom.pmf(8, n_trials, success_probability):.6f}")
print(f"Poisson probability of exactly 3 events (lambda=5): "
      f"{poisson.pmf(3, poisson_lambda):.6f}")

# ---------------------------------------------------------
# 5. SAMPLING TECHNIQUES
# ---------------------------------------------------------

random_sample = df.sample(n=min(100, len(df)), random_state=42)

stratified_sample = (
    df.groupby("Region", group_keys=False)
      .sample(frac=0.10, random_state=42)
)

systematic_interval = 10
systematic_sample = df.iloc[::systematic_interval]

sampling_summary = pd.DataFrame({
    "Sample": ["Full Dataset", "Random Sample",
               "Stratified Sample", "Systematic Sample"],
    "Record Count": [
        len(df), len(random_sample),
        len(stratified_sample), len(systematic_sample)
    ],
    "Average Sales": [
        df["Sales"].mean(),
        random_sample["Sales"].mean(),
        stratified_sample["Sales"].mean(),
        systematic_sample["Sales"].mean()
    ]
})

print("\nSAMPLING COMPARISON")
print("-------------------")
print(sampling_summary.to_string(index=False))
sampling_summary.to_csv(REPORTS_DIR / "sampling_comparison.csv", index=False)

# ---------------------------------------------------------
# 6. HYPOTHESIS TESTING
# ---------------------------------------------------------

alpha = 0.05
benchmark_mean = 200

one_sample_t, one_sample_p = stats.ttest_1samp(
    sales, popmean=benchmark_mean
)

east_sales = df.loc[df["Region"] == "East", "Sales"]
west_sales = df.loc[df["Region"] == "West", "Sales"]

independent_t, independent_p = stats.ttest_ind(
    east_sales, west_sales, equal_var=False
)

df["Profit_Status"] = np.where(
    df["Profit"] > 0, "Profitable", "Non-Profitable"
)
contingency_table = pd.crosstab(df["Region"], df["Profit_Status"])

chi2_stat, chi2_p, chi2_dof, expected_frequencies = (
    stats.chi2_contingency(contingency_table)
)

hypothesis_report = pd.DataFrame({
    "Test": [
        "One-Sample T-Test",
        "Independent T-Test (East vs West)",
        "Chi-Square Test (Region vs Profit Status)"
    ],
    "Test Statistic": [one_sample_t, independent_t, chi2_stat],
    "P-Value": [one_sample_p, independent_p, chi2_p],
    "Degrees of Freedom": [
        len(sales) - 1,
        np.nan,
        chi2_dof
    ],
    "Decision at 0.05": [
        "Reject H0" if one_sample_p < alpha else "Fail to reject H0",
        "Reject H0" if independent_p < alpha else "Fail to reject H0",
        "Reject H0" if chi2_p < alpha else "Fail to reject H0"
    ]
})

print("\nHYPOTHESIS TESTING")
print("------------------")
print(hypothesis_report.to_string(index=False))
print("\nChi-square expected frequencies:")
print(pd.DataFrame(
    expected_frequencies,
    index=contingency_table.index,
    columns=contingency_table.columns
))
hypothesis_report.to_csv(REPORTS_DIR / "hypothesis_testing_report.csv", index=False)

# ---------------------------------------------------------
# 7. CONFIDENCE INTERVAL
# ---------------------------------------------------------

standard_error = stats.sem(sales)
confidence_interval = stats.t.interval(
    confidence=0.95,
    df=len(sales) - 1,
    loc=sales.mean(),
    scale=standard_error
)

confidence_report = pd.DataFrame({
    "Metric": ["Mean Sales", "Lower 95% Confidence Limit",
               "Upper 95% Confidence Limit"],
    "Value": [sales.mean(), confidence_interval[0], confidence_interval[1]]
})

print("\n95% CONFIDENCE INTERVAL FOR MEAN SALES")
print("--------------------------------------")
print(f"Mean sales: {sales.mean():.2f}")
print(f"95% confidence interval: ({confidence_interval[0]:.2f}, "
      f"{confidence_interval[1]:.2f})")

confidence_report.to_csv(
    REPORTS_DIR / "confidence_interval_report.csv", index=False
)

plt.figure(figsize=(8, 4))
plt.errorbar(
    x=sales.mean(),
    y=1,
    xerr=[[
        sales.mean() - confidence_interval[0]
    ], [
        confidence_interval[1] - sales.mean()
    ]],
    fmt="o",
    capsize=8,
    markersize=8
)
plt.title("95% Confidence Interval for Average Sales")
plt.xlabel("Sales")
plt.yticks([])
plt.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "sales_confidence_interval.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 8. CORRELATION AND COVARIANCE
# ---------------------------------------------------------

correlation_data = df[["Sales", "Profit", "Quantity"]]
correlation_matrix = correlation_data.corr()

pearson_correlation = df["Sales"].corr(df["Profit"], method="pearson")
spearman_correlation = df["Sales"].corr(df["Profit"], method="spearman")
sales_profit_covariance = df["Sales"].cov(df["Profit"])

print("\nCORRELATION ANALYSIS")
print("--------------------")
print(correlation_matrix)
print(f"Pearson correlation (Sales and Profit): {pearson_correlation:.4f}")
print(f"Spearman correlation (Sales and Profit): {spearman_correlation:.4f}")
print(f"Covariance (Sales and Profit): {sales_profit_covariance:.2f}")

correlation_matrix.to_csv(REPORTS_DIR / "correlation_matrix.csv")

plt.figure(figsize=(8, 6))
sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    fmt=".2f",
    linewidths=0.5
)
plt.title("Correlation Heatmap")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "correlation_heatmap.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 9. BUSINESS PERFORMANCE ANALYSIS
# ---------------------------------------------------------

region_analysis = (
    df.groupby("Region")
      .agg(Sales=("Sales", "sum"),
           Profit=("Profit", "sum"),
           Quantity=("Quantity", "sum"))
      .reset_index()
)
region_analysis.to_csv(REPORTS_DIR / "regional_analysis.csv", index=False)

category_analysis = (
    df.groupby("Category")
      .agg(Sales=("Sales", "sum"),
           Profit=("Profit", "sum"),
           Quantity=("Quantity", "sum"))
      .reset_index()
)
category_analysis["Profit_Margin"] = (
    category_analysis["Profit"] / category_analysis["Sales"] * 100
)
category_analysis.to_csv(REPORTS_DIR / "category_analysis.csv", index=False)

subcategory_analysis = (
    df.groupby("Sub-Category")
      .agg(Sales=("Sales", "sum"),
           Profit=("Profit", "sum"),
           Quantity=("Quantity", "sum"))
      .reset_index()
      .sort_values("Profit", ascending=False)
)
subcategory_analysis.to_csv(
    REPORTS_DIR / "subcategory_analysis.csv", index=False
)

segment_analysis = (
    df.groupby("Segment")
      .agg(Sales=("Sales", "sum"),
           Profit=("Profit", "sum"),
           Quantity=("Quantity", "sum"))
      .reset_index()
)
segment_analysis["Profit_Margin"] = (
    segment_analysis["Profit"] / segment_analysis["Sales"] * 100
)
segment_analysis["Sales_Contribution"] = (
    segment_analysis["Sales"] / df["Sales"].sum() * 100
)
segment_analysis.to_csv(REPORTS_DIR / "segment_analysis.csv", index=False)

print("\nREGIONAL PERFORMANCE")
print("--------------------")
print(region_analysis.to_string(index=False))
print("\nCATEGORY PERFORMANCE")
print("--------------------")
print(category_analysis.to_string(index=False))
print("\nSUB-CATEGORY PERFORMANCE")
print("------------------------")
print(subcategory_analysis.to_string(index=False))
print("\nCUSTOMER SEGMENT PERFORMANCE")
print("----------------------------")
print(segment_analysis.to_string(index=False))

# Regional charts
for metric, filename, title, ylabel in [
    ("Sales", "regional_sales_analysis.png", "Total Sales by Region", "Total Sales"),
    ("Profit", "regional_profit_analysis.png", "Total Profit by Region", "Total Profit")
]:
    plt.figure(figsize=(9, 5))
    sns.barplot(data=region_analysis, x="Region", y=metric)
    plt.title(title)
    plt.xlabel("Region")
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename, dpi=150)
    plt.close()

# Category charts
for metric, filename, title, ylabel in [
    ("Sales", "category_sales_analysis.png", "Total Sales by Category", "Total Sales"),
    ("Profit", "category_profit_analysis.png", "Total Profit by Category", "Total Profit")
]:
    plt.figure(figsize=(9, 5))
    sns.barplot(data=category_analysis, x="Category", y=metric)
    plt.title(title)
    plt.xlabel("Category")
    plt.ylabel(ylabel)
    plt.xticks(rotation=10)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename, dpi=150)
    plt.close()

plt.figure(figsize=(12, 7))
sns.barplot(data=subcategory_analysis, x="Profit", y="Sub-Category")
plt.title("Profit Analysis by Sub-Category")
plt.xlabel("Total Profit")
plt.ylabel("Sub-Category")
plt.tight_layout()
plt.savefig(CHARTS_DIR / "subcategory_profit_analysis.png", dpi=150)
plt.close()

for metric, filename, title in [
    ("Sales", "segment_sales_analysis.png", "Total Sales by Customer Segment"),
    ("Profit", "segment_profit_analysis.png", "Total Profit by Customer Segment")
]:
    plt.figure(figsize=(9, 5))
    sns.barplot(data=segment_analysis, x="Segment", y=metric)
    plt.title(title)
    plt.xlabel("Customer Segment")
    plt.ylabel(f"Total {metric}")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename, dpi=150)
    plt.close()

# Monthly sales trend
monthly_sales = (
    df.groupby(["Year", "Month"])["Sales"]
      .sum()
      .reset_index()
)
monthly_sales["Period"] = (
    monthly_sales["Year"].astype(str) + "-"
    + monthly_sales["Month"].astype(str).str.zfill(2)
)
monthly_sales.to_csv(REPORTS_DIR / "monthly_sales_trend.csv", index=False)

plt.figure(figsize=(12, 5))
sns.lineplot(data=monthly_sales, x="Period", y="Sales", marker="o")
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(CHARTS_DIR / "monthly_sales_trend.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 10. EXECUTIVE KPIs AND DASHBOARD
# ---------------------------------------------------------

total_sales = df["Sales"].sum()
total_profit = df["Profit"].sum()
total_sales_records = len(df)  # Dataset has no unique Order ID column.
total_quantity = df["Quantity"].sum()
average_sales = df["Sales"].mean()
profit_margin = (total_profit / total_sales) * 100 if total_sales else 0

kpi_report = pd.DataFrame({
    "KPI": [
        "Total Sales",
        "Total Profit",
        "Total Sales Records",
        "Total Quantity Sold",
        "Average Sales",
        "Profit Margin"
    ],
    "Value": [
        total_sales,
        total_profit,
        total_sales_records,
        total_quantity,
        average_sales,
        profit_margin
    ]
})

print("\nEXECUTIVE DASHBOARD KPIs")
print("------------------------")
print(kpi_report.to_string(index=False))
kpi_report.to_csv(REPORTS_DIR / "business_kpis.csv", index=False)

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle("Superstore Sales – Executive Dashboard", fontsize=16)

kpi_items = [
    ("Total Sales", f"{total_sales:,.2f}"),
    ("Total Profit", f"{total_profit:,.2f}"),
    ("Total Sales Records", f"{total_sales_records:,}"),
    ("Quantity Sold", f"{total_quantity:,.0f}"),
    ("Average Sales", f"{average_sales:,.2f}"),
    ("Profit Margin", f"{profit_margin:.2f}%")
]

for ax, (label, value) in zip(axes.flat, kpi_items):
    ax.axis("off")
    ax.text(0.5, 0.62, value, ha="center", va="center",
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.35, label, ha="center", va="center", fontsize=11)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(CHARTS_DIR / "executive_kpi_dashboard.png", dpi=160)
plt.close()

# Combined dashboard: six panels
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle("Superstore Business Performance Dashboard", fontsize=18)

sns.barplot(data=region_analysis, x="Region", y="Sales", ax=axes[0, 0])
axes[0, 0].set_title("Regional Sales")

sns.barplot(data=region_analysis, x="Region", y="Profit", ax=axes[0, 1])
axes[0, 1].set_title("Regional Profit")

sns.barplot(data=category_analysis, x="Category", y="Sales", ax=axes[0, 2])
axes[0, 2].set_title("Category Sales")
axes[0, 2].tick_params(axis="x", rotation=15)

sns.barplot(data=category_analysis, x="Category", y="Profit", ax=axes[1, 0])
axes[1, 0].set_title("Category Profit")
axes[1, 0].tick_params(axis="x", rotation=15)

sns.lineplot(data=monthly_sales, x="Period", y="Sales",
             marker="o", ax=axes[1, 1])
axes[1, 1].set_title("Monthly Sales Trend")
axes[1, 1].tick_params(axis="x", rotation=45)

axes[1, 2].axis("off")
axes[1, 2].text(
    0.05, 0.85,
    f"TOTAL SALES\n{total_sales:,.2f}\n\n"
    f"TOTAL PROFIT\n{total_profit:,.2f}\n\n"
    f"SALES RECORDS\n{total_sales_records:,}\n\n"
    f"PROFIT MARGIN\n{profit_margin:.2f}%",
    fontsize=13, va="top"
)

plt.tight_layout(rect=[0, 0, 1, 0.95])
dashboard_path = CHARTS_DIR / "final_executive_dashboard.png"
plt.savefig(dashboard_path, dpi=160)
plt.close()

# Copy key visuals to screenshots for project documentation.
import shutil

for image_name in [
    "final_executive_dashboard.png",
    "sales_confidence_interval.png",
    "correlation_heatmap.png"
]:
    source = CHARTS_DIR / image_name
    if source.exists():
        shutil.copy2(source, SCREENSHOTS_DIR / image_name)

# ---------------------------------------------------------
# 11. EXCEL BUSINESS REPORT
# ---------------------------------------------------------

excel_path = REPORTS_DIR / "superstore_business_report.xlsx"

with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    kpi_report.to_excel(writer, sheet_name="Business KPIs", index=False)
    region_analysis.to_excel(writer, sheet_name="Regional Analysis", index=False)
    category_analysis.to_excel(writer, sheet_name="Category Analysis", index=False)
    confidence_report.to_excel(writer, sheet_name="Confidence Interval", index=False)
    hypothesis_report.to_excel(writer, sheet_name="Hypothesis Tests", index=False)
    correlation_matrix.to_excel(writer, sheet_name="Correlation Matrix")
    segment_analysis.to_excel(writer, sheet_name="Segment Analysis", index=False)

# ---------------------------------------------------------
# 12. PDF BUSINESS SUMMARY
# ---------------------------------------------------------

try:
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4

    pdf_path = REPORTS_DIR / "superstore_business_report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Superstore Sales – Business Summary", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Business KPI Summary", styles["Heading2"])
    ]

    kpi_table_data = [["KPI", "Value"]]
    for _, row in kpi_report.iterrows():
        value = row["Value"]
        if row["KPI"] in ["Total Sales", "Total Profit", "Average Sales"]:
            value = f"{value:,.2f}"
        elif row["KPI"] == "Profit Margin":
            value = f"{value:.2f}%"
        else:
            value = f"{value:,.0f}"
        kpi_table_data.append([row["KPI"], value])

    kpi_table = Table(kpi_table_data, hAlign="LEFT")
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))
    story.extend([kpi_table, Spacer(1, 12)])

    story.append(Paragraph("Regional Performance", styles["Heading2"]))
    region_table = [["Region", "Sales", "Profit"]]
    for _, row in region_analysis.iterrows():
        region_table.append([
            row["Region"], f'{row["Sales"]:,.2f}', f'{row["Profit"]:,.2f}'
        ])
    rt = Table(region_table, hAlign="LEFT")
    rt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5)
    ]))
    story.extend([rt, Spacer(1, 12)])

    story.append(Paragraph("Category Performance", styles["Heading2"]))
    category_table = [["Category", "Sales", "Profit", "Profit Margin"]]
    for _, row in category_analysis.iterrows():
        category_table.append([
            row["Category"],
            f'{row["Sales"]:,.2f}',
            f'{row["Profit"]:,.2f}',
            f'{row["Profit_Margin"]:.2f}%'
        ])
    ct = Table(category_table, hAlign="LEFT")
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9EAF7")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 5)
    ]))
    story.extend([ct, Spacer(1, 12)])

    story.append(Paragraph("Statistical Findings", styles["Heading2"]))
    story.append(Paragraph(
        f"95% confidence interval for mean sales: "
        f"{confidence_interval[0]:,.2f} to {confidence_interval[1]:,.2f}.",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "The chi-square test examines association between region and profit "
        "status; it does not establish causation. Correlation also describes "
        "association and should not be interpreted as proof of cause and effect.",
        styles["BodyText"]
    ))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Business Insights", styles["Heading2"]))
    story.append(Paragraph(
        "Technology recorded the highest category sales and profit in this "
        "dataset. Furniture had a comparatively low profit margin. The West "
        "region recorded the highest regional sales and profit. These findings "
        "can guide further investigation into product and regional performance.",
        styles["BodyText"]
    ))

    doc.build(story)

except ImportError:
    print("\nReportLab is not installed. PDF summary was not generated.")
    print("Install it with: pip install reportlab")

print("\nPROJECT RUN COMPLETED")
print("---------------------")
print(f"Charts saved in: {CHARTS_DIR}")
print(f"Reports saved in: {REPORTS_DIR}")
print(f"Screenshots saved in: {SCREENSHOTS_DIR}")
print("Python source code finished successfully.")
