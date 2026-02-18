from pathlib import Path

from great_tables import GT, style, loc
import polars as pl

# =============================================================================
# Story
# =============================================================================
# This week we're exploring the event schedule for the 2026 Winter Olympics in Milan-Cortina, Italy.
# The dataset contains detailed information about all 1,866 Olympic events, including both competition
# and training sessions across various winter sport disciplines.
# The dataset provides comprehensive scheduling information with start and end times in both local and
# UTC timezones, venue details, and metadata about each event such as whether it's a medal event or training session.
# This dataset captures the full scope of Olympic events taking place from early February through the closing ceremonies,
# including the new ski mountaineering event.
#
# - Which sport disciplines have the most events scheduled?
# - How are medal events distributed across the days of the Olympics?
# - What is the typical duration of different types of events?
# - Which venues host the most events?
# - How does the schedule vary by day of the week?
# - What proportion of scheduled sessions are training versus competition?
# =============================================================================

# Load the events data
dataset_url = "https://raw.githubusercontent.com/chendaniely/olympics-2026/refs/heads/main/data/final/olympics/olympics_events.csv"
olympic_events = pl.read_csv(dataset_url)

schedule = (
    olympic_events.group_by("date", "discipline_name")
    .agg(
        pl.len().alias("total_events"),
        pl.col("is_medal_event").sum().alias("medal_events"),
    )
    .sort("date", "discipline_name")
)

print(f"Schedule shape: {schedule.shape}")
print("\nFirst 20 rows:")
print(schedule.head(20))

schedule = schedule.with_columns(pl.col("date").str.to_date("%Y-%m-%d"))

print("Updated schema:")
print(schedule.schema)
print("\nFirst few rows:")
schedule.head(10)

# Pivot the schedule to have disciplines as rows and dates as columns
schedule_pivot = schedule.pivot(
    on="date",
    index="discipline_name",
    values="total_events",
).sort("discipline_name")

# Create the table
gt_table = (
    GT(schedule_pivot)
    .tab_header(
        title="Olympics 2026 Event Schedule",
        subtitle="Total events per sport by date",
    )
    .cols_label(discipline_name="Sport")
)

# Save to a temporary file and open in browser
gt_table.save("src/2026/20260210/table.png")
