import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from pyfonts import load_font

# =============================================================================
# DESIGN PHILOSOPHY
# =============================================================================
# Story: The number of languages natively spoken in Africa is variously estimated
# (depending on the delineation of language vs. dialect) at between 1,250 and 2,100
# and by some counts at over 3,000.
#
# The dataset is rich with information on the number of languages spoken across the continent.
# Some of the questions that could be thought of include:
#
# Which country in Africa has the largest number of spoken languages?
# Which family of languages has the highest density of speakers?
# Are there any languages that cut across multiple countries?
#
# Design principles:
# - Minimalist aesthetic to highlight the beauty of languages from africa.
# =============================================================================

# Load data
df = pl.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-01-13/africa.csv"
)

# Load fonts
font_regular = load_font(
    "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"
)
font_bold = load_font(
    "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Bold.ttf"
)

# print(df.head())
# print(len(df))
# print(df.unique("family"))

# # Top 10 Most Diverse Countries
# plt.figure(figsize=(10, 6))
# top_countries = (
#     df.group_by("country")["language"].count().sort_values(ascending=False).head(10)
# )
# sns.barplot(x=top_countries.values, y=top_countries.index, palette="magma")
# plt.title("The Polyglot Leaderboard: Top 10 Countries by Language Count")
# plt.xlabel("Number of Unique Languages")
# plt.show()

# # Language Family Speaker Distribution
# plt.figure(figsize=(8, 8))
# family_data = df.group_by("family")["native_speakers"].sum().sort_values(ascending=False)
# plt.pie(
#     family_data,
#     labels=family_data.index,
#     autopct="%1.1f%%",
#     colors=sns.color_palette("Set3"),
# )
# plt.title("Speaker Share by Language Family")
# plt.show()

# # Identifying Cross-Border Languages
# cross_border = df.group_by("language")["country"].n_unique()
# multi_nation = cross_border[cross_border > 1].sort_values(ascending=False).head(10)
# print("Top Cross-Border Languages:\n", multi_nation)


# Speaker Density per Family
# Density = Total Native Speakers / Number of Unique Languages in that family
density_df = (
    df.group_by("family")
    .agg(
        [
            pl.col("native_speakers").sum().alias("total_speakers"),
            pl.col("language").n_unique().alias("unique_languages_count"),
        ]
    )
    .with_columns(
        (pl.col("total_speakers") / pl.col("unique_languages_count")).alias(
            "speaker_density"
        )
    )
    .sort("speaker_density", descending=True)
)

# Cross-border Reach
# Which languages unite the most countries?
reach_df = (
    df.group_by("language")
    .agg(pl.col("country").n_unique().alias("country_count"))
    .filter(pl.col("country_count") > 1)
    .sort("country_count", descending=True)
)

# Linguistic Concentration (Entropy-like)
# How concentrated are speakers within a country?
country_concentration = (
    df.group_by("country")
    .agg(
        [
            pl.col("language").count().alias("lang_count"),
            pl.col("native_speakers").std().fill_null(0).alias("speaker_variance"),
        ]
    )
    .sort("lang_count", descending=True)
)

# --- Visualizations ---

# Plot 1: Speaker Density per Family
plt.figure(figsize=(12, 6))
sns.barplot(
    data=density_df.to_pandas(),
    x="speaker_density",
    hue="speaker_density",
    y="family",
    palette="flare",
)
plt.title(
    "Speaker Density: Which Language Families have the most 'Impact' per Language?",
    fontsize=14,
)
plt.xlabel("Average Native Speakers per Language")
plt.ylabel("Language Family")
plt.tight_layout()
plt.savefig("src/2026/20260113/speaker_density.png")

# Plot 2: Cross-border Reach
plt.figure(figsize=(12, 6))
sns.barplot(
    data=reach_df.to_pandas().head(10),
    x="country_count",
    hue="country_count",
    y="language",
    palette="crest",
)
plt.title(
    "Bridges of the Continent: Top 10 Languages Spoken in Multiple Countries",
    fontsize=14,
)
plt.xlabel("Number of Countries")
plt.ylabel("Language")
plt.tight_layout()
plt.savefig("src/2026/20260113/cross_border_reach.png")

# Plot 3: Linguistic Concentration
plt.figure(figsize=(12, 6))
sns.scatterplot(
    data=country_concentration.to_pandas(),
    x="lang_count",
    y="speaker_variance",
    hue="lang_count",
    size="lang_count",
    palette="viridis",
    sizes=(50, 500),
    legend=False,
)
plt.title(
    "Linguistic Concentration: Diversity vs. Speaker Variance by Country", fontsize=14
)
plt.xlabel("Number of Languages Spoken")
plt.ylabel("Variance in Native Speakers")
plt.tight_layout()
plt.savefig("src/2026/20260113/linguistic_concentration.png")

# Diversity of Language Families per Country
# We want to know how many distinct 'branches' of humanity are in one place.
country_diversity = (
    df.group_by("country")
    .agg(
        [
            pl.col("family").n_unique().alias("family_diversity"),
            pl.col("language").count().alias("total_languages"),
        ]
    )
    .sort("family_diversity", descending=True)
)

# Load Geographical Data, To be downloaded separately
# You can get the original 'naturalearth_lowres' data from https://www.naturalearthdata.com/downloads/110m-cultural-vectors/.
world = gpd.read_file("data/ne_110m_admin_0_countries.shp")
africa = world[world["CONTINENT"] == "Africa"]

# Join Polars Data with Map Data
# We convert Polars to Pandas just for the merge with GeoPandas
map_data = world.merge(
    country_diversity.to_pandas(), left_on="ADMIN", right_on="country", how="left"
)

# 5. Plotting the Geographical Map
fig, ax = plt.subplots(1, 1, figsize=(15, 10))
# Plot missing data in light grey
africa.plot(ax=ax, color="#eeeeee", edgecolor="#ffffff")
# Plot the diversity index
map_data.plot(
    column="family_diversity",
    ax=ax,
    legend=True,
    legend_kwds={
        "label": "Number of Unique Language Families",
        "orientation": "horizontal",
    },
    cmap="YlGnBu",
    edgecolor="white",
    linewidth=0.5,
)
ax.set_title(
    "The African Linguistic Mosaic: Deep Family Diversity by Country", fontsize=20
)
ax.axis("off")
plt.savefig("src/2026/20260113/output.png")
