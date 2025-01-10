import streamlit as st
import altair as alt
from requests.exceptions import ChunkedEncodingError
import pandas as pd
import plotly.express as px
import fungsiumum as fu
from datetime import datetime

from itables.streamlit import interactive_table


# Time-Series Analysis
st.markdown("## Analisa Kunjungan Per Hari")

dfh = fu.load_users('hits.csv')

# Aggregating data by date
# Ensure 'hit_time' is in datetime format
dfh['hit_time'] = pd.to_datetime(dfh['hit_time'], errors='coerce')

# Handle any invalid conversions (if 'errors="coerce"', non-datetime entries will become NaT)
if dfh['hit_time'].isna().any():
    st.warning("Some entries in 'hit_time' could not be converted to datetime and were dropped.")
    dfh = dfh.dropna(subset=['hit_time'])

# Extract the date for aggregation
dfh['tanggal'] = dfh['hit_time'].dt.date  # Extract date from datetime
daily_visits = dfh.groupby('tanggal').size().reset_index(name='visit_count')


# Plotting the time-series
time_series_chart = alt.Chart(daily_visits).mark_line().encode(
    x=alt.X('tanggal:T', title='Tanggal'),
    y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
    tooltip=[
        alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
        alt.Tooltip('visit_count:Q', title='Kunjungan')
    ]
).properties(
    title="Kunjungan Per Hari",
    height=400,
    width=800
).interactive()

st.altair_chart(time_series_chart)

# Remove 'Other' and 'Unknown' from country and city
dfh = dfh[~dfh['country'].isin(["Other", "Unknown"])]
dfh = dfh[~dfh['city'].isin(["Other", "Unknown"])]

# Filters
st.markdown("### Filter Menurut Negara dan Kota")

# Country filter
selected_country = st.selectbox("Pilih Negara", options=['All'] + dfh['country'].unique().tolist(), index=0)

# Filter cities based on the selected country
if selected_country == 'All':
    filtered_cities = dfh['city'].unique()
else:
    filtered_cities = dfh[dfh['country'] == selected_country]['city'].unique()

# City filter
selected_city = st.selectbox("Pilih Kota", options=['All'] + sorted(filtered_cities), index=0)

# Apply both filters
if selected_country != 'All':
    dfh = dfh[dfh['country'] == selected_country]

if selected_city != 'All':
    dfh = dfh[dfh['city'] == selected_city]

# Aggregate filtered data
daily_visits_filtered = dfh.groupby('tanggal').size().reset_index(name='visit_count')

# Plot the filtered data
time_series_chart_filtered = alt.Chart(daily_visits_filtered).mark_line().encode(
    x=alt.X('tanggal:T', title='Tanggal'),
    y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
    tooltip=[
        alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
        alt.Tooltip('visit_count:Q', title='Kunjungan')
    ]
).properties(
    title="Daily Visits Over Time",
    height=400,
    width=800
).interactive()

st.altair_chart(time_series_chart_filtered)
