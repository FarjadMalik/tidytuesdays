import pandas as pd
import numpy as np
from plotly import express as px

# =============================================================================
# Story
# =============================================================================
# Strait of Hormuz is a narrow waterway that connects the Persian Gulf to the
# Gulf of Oman and the Arabian Sea. It is one of the most strategically important
# chokepoints in the world, as it is a major transit route for oil and gas shipments
# from the Middle East to global markets. The strait is only about 21 miles wide at
# its narrowest point, and it is estimated that around 20% of the world's oil passes
# through it each day. The Strait of Hormuz has been a source of tension between Iran
# and other countries in the region, as Iran has threatened to block the strait
# in response to economic sanctions and other political disputes.
# The situation in the Strait of Hormuz remains a significant concern for global energy
# security and international relations.
# Data from EIA, the Energy Information Administration (https://eia.gov), part of the US government
# https://www.eia.gov/international/data/world/petroleum-and-other-liquids/annual-crude-and-lease-condensate-exports
# =============================================================================

print(pd.__version__)

# Load the data
dataset_url = "data/CrudeOil_SeriesExport-03-08-2026-17-36-07.json"
# crude_df = pd.read_json(dataset_url)
# print(crude_df.head())
# print(crude_df.columns)

# Data is a list of dict
# Each element of data represents a different data point, each should probably be in a row of its own
# Explode method: It turns one row into a number of rows, putting each element of a list in a different row
crude_df = (
    pd.read_json(dataset_url)
    .explode("data")
    .assign(
        year=lambda df_: pd.to_datetime(df_["data"].str.get("date"), unit="ms").dt.year,
        value=pd.col("data").str.get("value"),
    )
    .replace({1: "production", 4: "export", "--": np.nan, "NA": np.nan})
    .assign(value=pd.col("value").astype(float))
    .set_index(["iso", "year"])[["activityid", "value"]]
    .drop("WORL", axis=0)
)

print(crude_df.head())
print(crude_df.columns)
print(len(crude_df))


persian_gulf_states = ["BHR", "IRN", "IRQ", "KWT", "QAT", "SAU", "ARE"]

(
    crude_df.loc[pd.col("activityid") == "export"]
    .pivot_table(columns="iso", index="year", values="value", aggfunc="sum")[
        persian_gulf_states
    ]
    .pipe(px.line)
).show()


print(
    crude_df.loc[pd.col("activityid") == "export"]
    .pivot_table(columns="iso", index="year", values="value", aggfunc="sum")[
        persian_gulf_states
    ]
    .iloc[-3]
    .mul(1000 * 80 * 365)
    .map("${:,}".format)
)
