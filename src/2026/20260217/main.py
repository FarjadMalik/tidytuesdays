import polars as pl
import matplotlib.pyplot as plt
from pypalettes import load_palette
from pyfonts import load_bunny_font

# =============================================================================
# Story
# =============================================================================
# This week we are exploring agriculture production statistics in New Zealand
# using data compiled from from StatsNZ. Sheep have long outnumbered people in
# New Zealand, but the ratio of sheep to people peaked in the 1980s and has been in
# steady decline
# The gap between people and sheep in New Zealand is rapidly closing. There's now
# about 4.5 sheep to every person in New Zealand compared to a peak of 22 sheep per
# person in the 1980s, that's according to figures released by Stats NZ this week.

# - Is sheep production unique in its decline? Do other types of meat production show the same pattern?
# - Which agricultural industries have shown the most production growth?
# =============================================================================

# Load the data
dataset_url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-02-17/dataset.csv"
agriculture_nz = pl.read_csv(dataset_url)

# Extract subset of data for relevant measures
# total sheep measure
total_sheep_df = agriculture_nz.filter(pl.col("measure") == "Total Sheep")
# farm area measure
farming_area_df = agriculture_nz.filter(pl.col("measure") == "Total Area of Farms")
# total dairy cattle measure
cattle_df = agriculture_nz.filter(
    pl.col("measure") == "Total Dairy Cattle (including Bobby Calves)"
)
beef_cattle_df = agriculture_nz.filter(pl.col("measure") == "Total Beef Cattle")
# fertilizer measure
# fertilizer_df = agriculture_nz.filter(pl.col("measure") == "Total All Fertilisers")

# Fill interpolated data for missing years

# Create the reference range (1935 to 2024 inclusive)
all_years = pl.int_range(1935, 2025, eager=True).alias("year_ended_june").to_frame()

# left join the total sheep data to the reference range to create a complete dataset for missing years
df_complete = all_years.join(total_sheep_df, on="year_ended_june", how="left")
# interpolate the missing values in the 'value' column using linear interpolation
total_sheep_df = df_complete.with_columns(pl.col("value").interpolate())
# fill constant columns that became null (measure, unit, etc)
total_sheep_df = total_sheep_df.with_columns(
    [
        pl.col("measure").fill_null("Total Sheep"),
        pl.col("value_unit").fill_null("number"),
        pl.col("value_label").fill_null("Number of sheep"),
    ]
)
# left join the total sheep data to the reference range to create a complete dataset for missing years
df_complete = all_years.join(farming_area_df, on="year_ended_june", how="left")
# interpolate the missing values in the 'value' column using linear interpolation
farming_area_df = df_complete.with_columns(pl.col("value").interpolate())
# fill constant columns that became null (measure, unit, etc)
farming_area_df = farming_area_df.with_columns(
    [
        pl.col("measure").fill_null("Total Area of Farms"),
        pl.col("value_unit").fill_null("number"),
        pl.col("value_label").fill_null("Hectares"),
    ]
)

# foward fill nulls for cattle measures
# take previous cattle for missing values
all_years = pl.int_range(1971, 2025, eager=True).alias("year_ended_june").to_frame()
cattle_df = all_years.join(cattle_df, on="year_ended_june", how="left")
cattle_df = cattle_df.with_columns(
    [
        pl.col("value").fill_null(strategy="forward"),
        pl.col("measure").fill_null("Total Dairy Cattle (including Bobby Calves)"),
        pl.col("value_unit").fill_null("number"),
        pl.col("value_label").fill_null("Number of cattle"),
    ]
)
beef_cattle_df = all_years.join(beef_cattle_df, on="year_ended_june", how="left")
beef_cattle_df = beef_cattle_df.with_columns(
    [
        pl.col("value").fill_null(strategy="forward"),
        pl.col("measure").fill_null("Total Beef Cattle"),
        pl.col("value_unit").fill_null("number"),
        pl.col("value_label").fill_null("Number of cattle"),
    ]
)

peak_idx = farming_area_df["value"].arg_max()
farming_peak_year = farming_area_df["year_ended_june"][peak_idx]
farming_peak_val = farming_area_df["value"][peak_idx]
print(f"Farming peak (idx: {peak_idx}) at {farming_peak_val} in {farming_peak_year}")


# Plotting

# load assets
# fonts
font_regular = load_bunny_font("Actor", weight="regular")
font_bold = load_bunny_font("Actor", weight="bold")
font_fancy = load_bunny_font("Barrio")
font_fancy_bold = load_bunny_font("Barrio", weight="bold")

# colors
palette = load_palette("excel_Green")
farm_color = palette[1]
sheep_color = palette[5]
cattle_color = palette[4]


# create plot
fig, ax = plt.subplots(figsize=(12, 7), dpi=150)

# sheep
ax.plot(
    total_sheep_df["year_ended_june"],
    total_sheep_df["value"],
    color=sheep_color,
    linewidth=2,
    alpha=0.9,
)

# farm
ax.plot(
    farming_area_df["year_ended_june"],
    farming_area_df["value"],
    color=farm_color,
    linewidth=2,
    alpha=0.9,
)

# cattle
ax.plot(
    cattle_df["year_ended_june"],
    cattle_df["value"],
    color=cattle_color,
    linewidth=2,
    alpha=0.9,
)

ax.plot(
    beef_cattle_df["year_ended_june"],
    beef_cattle_df["value"],
    color=cattle_color,
    linewidth=2,
    alpha=0.9,
)

# annotation
# vertical span
ax.axvspan(
    1985,
    2024,
    color="gray",
    alpha=0.05,
    label="Farming in decline (and so the farming animals)",
)

# narrative text
story_text = (
    "In 1985, NZ hit 'Peak Farming area' (21M hec).\n"
    "Following 1984 economic reforms,\n"
    "stock numbers plummeted as farmers\n"
    "diversified and urbanized."
)
ax.text(
    1990,
    60_000_000,
    story_text,
    fontproperties=font_regular,
    fontsize=10,
    color="#444444",
    bbox=dict(facecolor="none", edgecolor="#cccccc", pad=10),
)

# fix spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#cccccc")
ax.spines["bottom"].set_color("#cccccc")
# subtle grid for readability
ax.grid(axis="y", linestyle="--", alpha=0.3)

# titles and labels
ax.set_title(
    "Comparison of Agricultural Data - NZ",
    fontsize=18,
    fontweight="bold",
    pad=20,
    loc="left",
)
ax.set_xlabel("Year", fontsize=12, labelpad=10)
ax.set_ylabel("Value", fontsize=12, labelpad=10)
# ax.legend(loc='upper right', frameon=False, fontsize=12)

# ticks
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontproperties(font_regular)
    label.set_color("#555555")

# display
plt.tight_layout()
plt.savefig("src/2026/20260217/output.png", dpi=300)
