import polars as pl
import plotly.express as px

# =============================================================================
# Story
# =============================================================================
# This week we're exploring the properties of various edible plants.
# =============================================================================

# Load data
edible_plants = pl.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-02-03/edible_plants.csv"
)


# Polars logic to calculate pH spread
ph_analysis = edible_plants.with_columns(
    [
        ((pl.col("preferred_ph_upper") + pl.col("preferred_ph_lower")) / 2).alias(
            "ph_mid"
        ),
        (pl.col("preferred_ph_upper") - pl.col("preferred_ph_lower")).alias("ph_range"),
    ]
).sort("ph_mid")

# The pH "Growth Window" (High-Low Chart)
# In botany, the pH range determines nutrient bioavailability.
# Let's visualize the "comfort zone" for each plant using a horizontal bar chart that shows the spread
# between preferred_ph_lower and preferred_ph_upper.
# We calculate the mid-point for sorting and the range for the error bar
fig = px.scatter(
    ph_analysis.to_pandas(),  # Plotly plays best with the .to_pandas() view
    x="ph_mid",
    y="common_name",
    error_x="ph_range",
    color="sunlight",
    title="Botanical pH Tolerance Windows",
    labels={"ph_mid": "Preferred pH (Midpoint)", "common_name": "Plant Species"},
    template="plotly_white",
)

fig.update_layout(height=600)
fig.write_image("src/2026/20260203/ph_tolerance_windows.png")


# Sunlight vs. Water Requirements (Heatmap/Sunburst)
# These are categorical variables. To see which environmental "profiles" are most common
# (e.g., how many plants need Full Sun + Low Water), we can create a heatmap or a sunburst chart.
# In the field, we often group plants by their cultivation requirements.
# This Sunburst chart is the perfect way to visualize the "Taxonomic Hierarchy" of your garden's needs.
# Aggregate counts using Polars
habit_counts = edible_plants.group_by(["cultivation", "sunlight", "water"]).agg(
    pl.len().alias("species_count")
)

fig = px.sunburst(
    habit_counts.to_pandas(),
    path=["cultivation", "sunlight", "water"],
    values="species_count",
    title="Ecological Niche Distribution",
    color_discrete_sequence=px.colors.qualitative.Dark24,
)
fig.write_image("src/2026/20260203/ecological_niche_distribution.png")


# A more "Polars-friendly" way to handle the ranges
def parse_botanical_range(col_name):
    return (
        pl.col(col_name)
        .str.extract_all(r"(\d+\.?\d*)")
        .map_elements(
            # Using a list comprehension and checking length safely
            lambda x: (
                sum(float(i) for i in x) / len(x)
                if (x is not None and len(x) > 0)
                else None
            ),
            return_dtype=pl.Float64,
        )
    )


# Now, let's process the garden
edible_plants_clean = edible_plants.with_columns(
    [
        parse_botanical_range("days_harvest").alias("days_to_harvest_avg"),
        parse_botanical_range("days_germination").alias("days_to_germinate_avg"),
        # Casting pH safely
        pl.col("preferred_ph_lower").cast(pl.Float64),
        pl.col("preferred_ph_upper").cast(pl.Float64),
    ]
).to_pandas()


fig = px.histogram(
    edible_plants_clean,
    x="days_to_harvest_avg",
    nbins=20,
    title="Distribution of Harvest Timelines",
    color="cultivation",
    labels={"days_to_harvest_avg": "Average Days until Harvest"},
    template="plotly_white",
)
fig.write_image("src/2026/20260203/harvest_timelines.png")
