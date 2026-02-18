import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
# Story
# =============================================================================
# A collection of socially impactful and visually stunning plots
# for analyzing company characteristics and relationships
# =============================================================================

# Load data
companies = pl.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-01-27/companies.csv"
)

# Capital Stock by size
companies_by_size = (
    companies.group_by("company_size")
    .agg(
        [
            pl.col("capital_stock").mean().alias("mean_capital"),
            pl.col("capital_stock").median().alias("median_capital"),
            pl.col("capital_stock").skew().alias("skewness"),
            pl.col("capital_stock").std().alias("std_dev"),
        ]
    )
    .sort("mean_capital")
)

# Company size analysis

# Visualization using Seaborn/Matplotlib
plt.figure(figsize=(12, 6))

# Subplot 1: Distribution Range
plt.subplot(1, 2, 1)
sns.boxplot(
    data=companies.to_pandas(),
    x="company_size",
    hue="company_size",
    y="capital_stock",
    palette="viridis",
)
plt.yscale("log")
plt.title("Capital Stock Range by Size (Log Scale)")
plt.ylabel("Capital Stock (BRL)")

# Subplot 2: Skewness/Density
plt.subplot(1, 2, 2)
for size in companies["company_size"].unique():
    subset = companies.filter(pl.col("company_size") == size)
    sns.kdeplot(
        subset["capital_stock"].to_numpy(), label=size, fill=True, log_scale=True
    )

plt.title("Skewness Density (Log Scale)")
plt.xlabel("Capital Stock (BRL)")
plt.legend()
plt.suptitle("Company Size Analysis - No real difference in stocks", fontsize=16)
plt.tight_layout()
plt.subplots_adjust(bottom=0.12, top=0.88)
plt.savefig(
    "src/2026/20260127/companysize_analysis.png",
    dpi=150,
    bbox_inches="tight",
    pad_inches=0.3,
)
plt.close()

# # Legal Nature Analysis
# legal_stats = (
#     companies.group_by("legal_nature")
#     .agg([
#         pl.col("capital_stock").sum().alias("total_capital"),
#         pl.col("capital_stock").mean().alias("avg_capital"),
#         pl.col("company_id").count().alias("count")
#     ])
#     .sort("total_capital", descending=True)
# )
# print(legal_stats)

# Top percentile analysis
top_10_percent = companies.filter(
    pl.col("capital_stock") >= companies["capital_stock"].quantile(0.90)
)


def get_category_concentration(df, col_name, percentile=0.90):
    return (
        df.group_by(col_name)
        .agg(
            [
                pl.col("capital_stock").sum().alias("total_cap"),
                # Filter the sum to only include those >= the specified percentile OF THAT GROUP
                pl.col("capital_stock")
                .filter(
                    pl.col("capital_stock")
                    >= pl.col("capital_stock").quantile(percentile)
                )
                .sum()
                .alias("tail_cap"),
            ]
        )
        .select(
            [
                pl.lit(col_name).alias("Category"),
                pl.col(col_name).alias("Value"),
                (pl.col("tail_cap") / pl.col("total_cap")).alias("Concentration"),
            ]
        )
        .sort("Concentration", descending=True)
    )


nature_concentration = get_category_concentration(companies, "legal_nature")
ownership_concentration = get_category_concentration(companies, "owner_qualification")
size_concentration = get_category_concentration(companies, "company_size")

# Plot concentration data

fig, axes = plt.subplots(2, 2, figsize=(18, 14))
sns.set_theme(style="whitegrid")

# Legal Nature
sns.barplot(
    data=nature_concentration.to_pandas(),
    x="Concentration",
    y="Value",
    hue="Value",
    ax=axes[0, 0],
    palette="viridis",
)
axes[0, 0].set_title("Composition of Top Tail (by Legal Nature)")

# Size Concentration

sns.barplot(
    data=size_concentration.to_pandas(),
    x="Concentration",
    y="Value",
    hue="Value",
    ax=axes[0, 1],
    palette="magma",
)
axes[0, 1].set_title("Size Distribution within the Top Tail")

# Owner Qualification Share
sns.barplot(
    data=ownership_concentration.to_pandas(),
    x="Concentration",
    y="Value",
    hue="Value",
    ax=axes[1, 0],
    palette="rocket",
)
axes[1, 0].set_title("Owner Qualification Distribution in Top Tail")

# Density Plot of Capital Stock by Company Size
for size in companies["company_size"].unique():
    subset = companies.filter(pl.col("company_size") == size)
    sns.kdeplot(
        subset["capital_stock"].to_numpy(),
        label=size,
        fill=True,
        log_scale=True,
        ax=axes[1, 1],
    )
axes[1, 1].set_title("Concentration: Capital Stock Companies by Size")

plt.tight_layout()
plt.savefig(
    "src/2026/20260127/output.png",
    dpi=150,
    bbox_inches="tight",
    pad_inches=0.3,
)
plt.close()
