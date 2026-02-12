import pandas as pd
from plotly import express as px

filename = "data/CPI2025_Results.xlsx"

cpi = pd.read_excel(
    filename, sheet_name="CPI2025", engine="calamine", header=3, usecols=[0, 1, 2, 3, 4]
)

fig = cpi.assign(reverse_rank=pd.col("Rank").max() - pd.col("Rank")).pipe(
    px.choropleth,
    locations="Country / Territory",
    locationmode="country names",
    color="reverse_rank",
    title="Corruption 2025",
    projection="robinson",
    hover_data=["CPI 2025 score", "Rank"],
)

fig.write_html("src\\then_some\\corruption_index.html")

# Show the names of the most and least corrupt countries in each region, using the CPI score.
# Show the highest and lowest CPI scores for these most/least corrupt countries, and the difference between them.
# How big is the most/least difference in each region?
(
    cpi.set_index("Country / Territory")
    .groupby(["Region"])["CPI 2025 score"]
    .agg(["min", "max", "idxmin", "idxmax"])
)
