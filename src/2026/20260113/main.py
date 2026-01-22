import polars as pl
import matplotlib.pyplot as plt
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

# # Load fonts
# font_regular = load_font(
#     "https://github.com/google/fonts/raw/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf"
# )
# font_bold = load_font(
#     "https://github.com/google/fonts/raw/main/ofl/spacemono/SpaceMono-Bold.ttf"
# )

print(df.head())
print(len(df))
print(df.unique("family"))
