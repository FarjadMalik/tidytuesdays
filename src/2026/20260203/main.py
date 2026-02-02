import polars as pl

# =============================================================================
# DESIGN PHILOSOPHY
# =============================================================================
# Story:
#
# Design principles:
# -
# =============================================================================

# Load data
edible_plants = pl.read_csv(
    "https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2026/2026-02-03/edible_plants.csv"
)
