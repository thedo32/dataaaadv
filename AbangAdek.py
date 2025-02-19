import streamlit as st
import altair as alt
from requests.exceptions import ChunkedEncodingError
import pandas as pd
import plotly.express as px
import fungsiumum as fu
from datetime import datetime
from geopy.geocoders import Nominatim
import requests
import json

from itables.streamlit import interactive_table

st.set_page_config(
    page_title="Abang Adek Data Analisis",
    page_icon="fishtail.png",
    layout="wide",
    menu_items={"About": """##### Batigo Data Analisis. 
            Author: Database Outlet
Email: databaseoutlet@gmail.com
            """}
)

# CSS to customize the delta color for Streamlit's metric component
st.markdown("""
    <style>
    /* Import custom fonts */
    @import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Protest+Guerrilla&family=Tilt+Neon&display=swap');

    /* Apply the custom font globally */
    html, body, div, [class*="css"] {
        font-family: 'Tilt Neon', sans-serif !important;
    }

    /* Apply custom color to Streamlit metric delta */
    div[data-testid="stMetricDelta"] {
        color: #A7D129 !important;
    }
    </style>
    """, unsafe_allow_html=True)



urluser = "https://restful.abangadek-adv.com/users"
urlhit = "https://restful.abangadek-adv.com/hits"


st.markdown("<h1 style='text-align: center;'>Analisa Data Abang Adek Advertising</h1>",unsafe_allow_html=True)

with st.expander("Ekspor Data Ke CSV"):
    # Dropdown to select the data to export
    export_option = st.selectbox(
        "Pilih Data untuk Diekspor ke CSV:",
        options=["Ekspor User Data", "Ekspor Hit Data"],
    )

    # Handle export based on selection
    if export_option == "Ekspor User Data":
        fu.users_csv("users.csv")
        st.success("User data telah diekspor ke 'users.csv'.")

    elif export_option == "Ekspor Hit Data":
        fu.hits_csv("hits.csv")
        st.success("Hit data telah diekspor ke 'hits.csv'.")


#dfu = fu.load_users('users.csv')
#dfh = fu.load_hits('hits.csv')

dfu = fu.fetch_data_user(urluser)
dfh = fu.fetch_data_hit(urlhit)


if dfu is None:
    dfu = fu.load_users('users.csv')
    if dfu is None:
        st.warning("Data tidak tersedia")

if dfh is None:
    dfh = fu.load_hits('hits.csv')
    if dfh is None:
        st.warning("Data tidak tersedia")

dfh["hit_time"] = pd.to_datetime(dfh["hit_time"], errors="coerce")

# Inject CSS for column styling
st.markdown(
    """
    <style>
    .column {
        border: 1px solid #cccccc;
        padding: 10px;
        border-radius: 5px;
        background-color: #000000;
        color: #ffffff;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Overall metric
# Assume dfh is already loaded and preprocessed
dfh['hit_time'] = pd.to_datetime(dfh['hit_time'], errors='coerce')
#dfh['hit_day'] = dfh['hit_time'].dt.date  # Extract the date part for grouping

st.markdown("## Data Jumlah Pengunjung")
# Main columns for metrics
col1, col2, col3 = st.columns(3, border=True)

# Total unique visitors

with col1:
    dfh_non_zero = dfh[dfh["user_id"] > 0]
    unique_logged_in_visitors = dfh_non_zero.groupby(['user_id', 'ip_address']).ngroups
    zero_count = dfh[dfh["user_id"] == 0]["id"].count()

    total_unique_visitors = unique_logged_in_visitors + zero_count
    st.metric(label="Jumlah Pengunjung", value=total_unique_visitors)

# Logged-in visitors (user_id > 0)
with col2:
    dfh_non_zero = dfh[dfh["user_id"] > 0]
    unique_logged_in_visitors = dfh_non_zero.groupby(['user_id', 'ip_address']).ngroups
    st.metric(label="Jumlah Pengunjung Login", value=unique_logged_in_visitors)

# Guest visitors (user_id == 0)
with col3:
    #dfh_zero = dfh[dfh["user_id"] == 0]
    #unique_guest_visitors = dfh_zero.groupby(['user_id', 'ip_address']).ngroups
    #st.metric(label="Jumlah Pengunjung Guest", value=unique_guest_visitors)

    # Count all hits for guest users without applying uniqueness
    zero_count = dfh[dfh["user_id"] == 0]["id"].count()
    st.metric(label="Jumlah Pengunjung Guest", value=zero_count)

# Yearly metrics
col4, col5, col6 = st.columns(3, border=True)
current_year = datetime.now().year
previous_year = current_year - 1

dfh_now = dfh[dfh["hit_time"].dt.year == current_year]
dfh_prev = dfh[dfh["hit_time"].dt.year == previous_year]

with col4:
    non_zero_count = dfh_now[dfh_now["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    non_prev_count = dfh_prev[dfh_prev["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    zero_count = dfh_now[dfh_now["user_id"] == 0]["id"].count()
    zero_prev = dfh_prev[dfh_prev["user_id"] == 0]["id"].count()

    total_count = non_zero_count + zero_count
    total_prev = non_prev_count + zero_prev
    delta = ((total_count - total_prev) / total_prev * 100) if total_prev != 0 else 0
    st.metric(label="Jumlah Pengunjung (Tahun Ini)", value=total_count, delta=f"{delta:.2f}%")

with col5:
    non_zero_count = dfh_now[dfh_now["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    non_prev_count = dfh_prev[dfh_prev["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    delta = ((non_zero_count - non_prev_count) / non_prev_count * 100) if non_prev_count != 0 else 0
    st.metric(label="Jumlah Pengunjung Login (Tahun Ini)", value=non_zero_count, delta=f"{delta:.2f}%")

with col6:
    #zero_count = dfh_now[dfh_now["user_id"] == 0].groupby(['user_id', 'ip_address']).ngroups
    #zero_prev = dfh_prev[dfh_prev["user_id"] == 0].groupby(['user_id', 'ip_address']).ngroups

    #count the guest witout uniqueness
    zero_count = dfh_now[dfh_now["user_id"] == 0]["id"].count()
    zero_prev = dfh_prev[dfh_prev["user_id"] == 0]["id"].count()

    delta = ((zero_count - zero_prev) / zero_prev * 100) if zero_prev != 0 else 0
    st.metric(label="Jumlah Pengunjung Guest (Tahun Ini)", value=zero_count, delta=f"{delta:.2f}%")

# Monthly metrics
col7, col8, col9 = st.columns(3, border=True)
now = datetime.now()
current_month = now.month
previous_month = current_month - 1
current_year = now.year
previous_year = current_year if previous_month > 0 else current_year - 1
if previous_month == 0:
    previous_month = 12

dfh_current_month = dfh[
    (dfh["hit_time"].dt.month == current_month) & (dfh["hit_time"].dt.year == current_year)
]
dfh_previous_month = dfh[
    (dfh["hit_time"].dt.month == previous_month) & (dfh["hit_time"].dt.year == previous_year)
]

with col7:
    non_zero_count = dfh_current_month[dfh_current_month["user_id"] > 0].groupby(
        ['user_id', 'ip_address']).ngroups
    non_prev_count = dfh_previous_month[dfh_previous_month["user_id"] > 0].groupby(
        ['user_id', 'ip_address']).ngroups

    zero_count = dfh_current_month[dfh_current_month["user_id"] == 0]["id"].count()
    zero_prev = dfh_previous_month[dfh_previous_month["user_id"] == 0]["id"].count()

    total_count = non_zero_count + zero_count
    total_prev = non_prev_count + zero_prev
    delta = ((total_count - total_prev) / total_prev * 100) if total_prev != 0 else 0
    st.metric(label="Jumlah Pengunjung (Bulan Ini)", value=total_count, delta=f"{delta:.2f}%")

with col8:
    non_zero_count = dfh_current_month[dfh_current_month["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    non_prev_count = dfh_previous_month[dfh_previous_month["user_id"] > 0].groupby(['user_id', 'ip_address']).ngroups
    delta = ((non_zero_count - non_prev_count) / non_prev_count * 100) if non_prev_count != 0 else 0
    st.metric(label="Jumlah Pengunjung Login (Bulan Ini)", value=non_zero_count, delta=f"{delta:.2f}%")

with col9:
    #zero_count = dfh_current_month[dfh_current_month["user_id"] == 0].groupby(['user_id', 'ip_address']).ngroups
    #zero_prev = dfh_previous_month[dfh_previous_month["user_id"] == 0].groupby(['user_id', 'ip_address']).ngroups
    #delta = ((zero_count - zero_prev) / zero_prev * 100) if zero_prev != 0 else 0
    #st.metric(label="Jumlah Pengunjung Guest (Bulan Ini)", value=zero_count, delta=f"{delta:.2f}%")

    #count guest without uniqueness
    zero_count = dfh_current_month[dfh_current_month["user_id"] == 0]["id"].count()
    zero_prev = dfh_previous_month[dfh_previous_month["user_id"] == 0]["id"].count()

    # Avoid division by zero
    delta = ((zero_count - zero_prev) / zero_prev * 100) if zero_prev != 0 else 0
    st.metric(label="Jumlah Pengunjung Guest (Bulan Ini)", value=zero_count, delta=f"{delta:.2f}%")

st.divider()

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


# Define tab names
tabs = ["Jumlah Kunjungan per Wilayah", "Jumlah Kunjungan per Halaman",  "Jumlah Kunjungan Halaman per Referensi Asal",
         "Jumlah Kunjungan Halaman per Tautan Asal", "Jumlah Kunjungan per Referensi Asal",  "Jumlah Kunjungan per Tautan Asal", "Pengguna Terdaftar"]

# Add a selectbox to switch between tabs
selected_tab = st.selectbox("Pilih Data Yang Akan Ditampilkan", tabs,
                            index=None, placeholder="Pilih Data...",)

if selected_tab == "Jumlah Kunjungan per Wilayah":
    # DAILY TIME ANALYSYS

    st.markdown("### Analisa Kunjungan Per Hari Berdasarkan Negara dan Kota")

    # Filter out "Other" and "Unknown"
    dfh = dfh[~dfh['country'].isin(["Other", "Unknown"])]
    dfh = dfh[~dfh['city'].isin(["Other", "Unknown"])]


    # Multiselect for country
    selected_countries = st.multiselect(
        "Pilih Negara",
        options=["All"] + dfh['country'].unique().tolist(),
        default=["All"],
    )

    # Filter based on selected countries
    if "All" not in selected_countries:
        dfh = dfh[dfh['country'].isin(selected_countries)]

    # Multiselect for city
    filtered_cities = dfh['city'].unique()
    selected_cities = st.multiselect(
        "Pilih Kota",
        options=["All"] + sorted(filtered_cities),
        default=["All"],
    )

    # Filter based on selected cities
    if "All" not in selected_cities:
        dfh = dfh[dfh['city'].isin(selected_cities)]

    # Aggregate filtered data
    daily_visits_filtered = dfh.groupby('tanggal').size().reset_index(name='visit_count')

    # Plot the filtered data
    if not daily_visits_filtered.empty:
        time_series_chart_filtered = alt.Chart(daily_visits_filtered).mark_line(point=True).encode(
            x=alt.X('tanggal:T', title='Tanggal'),
            y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
            tooltip=[
                alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
                alt.Tooltip('visit_count:Q', title='Kunjungan')
            ]
        ).properties(
            title="Kunjungan Per Hari Berdasarkan Wilayah",
            height=400,
            width=1200
        ).interactive()
        st.altair_chart(time_series_chart_filtered)
    else:
        st.warning("Tidak ada  data tersedia untuk filters yang dipilih.")

    st.divider()

    st.markdown("## Kunjungan Per Wilayah")
    # Altair Bar Chart for All Countries

    # filter other or unknown
    df = dfh[~dfh['city'].isin(["Other", "Unknown"])]

    all_countries = df['country'].unique().tolist()

    selection = alt.selection_point(fields=['country'], bind='legend')


    df = df.copy()
    df['trunc_city'] = df['city'].apply(lambda x: x if len(x) <= 10 else x[:10] + '...')

    colD, colE, colF = st.columns(3)
    with colD:
        st.markdown("<h3 style='text-align: center;'>Top 10 Kota</h3>", unsafe_allow_html=True)


        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_cities = df['city'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = df[df['city'].isin(top_10_cities)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_city:N",
                title=("Top 10 Kota"),
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["city", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)


    with colE:
        st.markdown("<h3 style='text-align: center;'>Top 10 Kota Indonesia</h3>", unsafe_allow_html=True)

        # Filter rows where the country is "Indonesia"
        indonesia_cities = df[df['country'] == 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_cities = indonesia_cities['city'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = indonesia_cities[indonesia_cities['city'].isin(top_10_cities)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_city:N",
                title="Nama Kota",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=[ "city", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    with colF:
        st.markdown("<h3 style='text-align: center;'>Top 10 Kota Luar Negeri</h3>", unsafe_allow_html=True)

        # Filter rows where the country is outside "Indonesia"
        abroad_cities = df[df['country'] != 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_cities = abroad_cities['city'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = abroad_cities[abroad_cities['city'].isin(top_10_cities)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_city:N",
                title="Nama Kota",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["city", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    with st.expander("Tampilkan Data Seluruh Negara"):
        with st.container():
            bars = alt.Chart(df).mark_bar(size=6).encode(
                x=alt.X(
                    "city:N",
                    title="Nama Kota",
                    axis=alt.Axis(labelAngle=90),
                    sort=alt.EncodingSortField(field="id", op="count", order="descending")
                ),
                y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
                xOffset=alt.X("country:N", title="Country"),  # Group by country
                color=alt.Color(
                    "country:N",
                    title="Negara",
                    scale=alt.Scale(domain=all_countries),  # Explicitly set domain
                    legend=alt.Legend(title="Pilih Negara")
                ),  # Different colors for each country
                tooltip=["country", "city", "count(id)"]  # Add tooltips for interactivity
            ).add_params(selection).transform_filter(selection).properties(
                height=800,
                width=1200
            ).interactive(bind_x=True, bind_y=True)

            st.altair_chart(bars, use_container_width=True)

    st.divider()

    #still in tab1
    # Geographic Heatmap by Country
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Negara")

    # Aggregate visit data by country and city
    country_visits = dfh.groupby('country').size().reset_index(name='visit_count')
    city_visits = dfh.groupby(['country', 'city']).size().reset_index(name='visit_count')

    # # Load GeoJSON for country polygons (example file: can be replaced with an actual GeoJSON URL)
    # geojson_url = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    # # with open('path_to_geojson_file.geojson', 'r') as file:
    # #     geojson_data = json.load(file)

    # # Match country names with GeoJSON property
    # fig_country = px.choropleth_mapbox(
    #     country_visits,
    #     geojson=geojson_url,
    #     locations='country',
    #     featureidkey='properties.name',  # Match with GeoJSON country names
    #     color='visit_count',
    #     hover_name='country',
    #     color_continuous_scale='Spectral',
    #     title="Peta Kunjungan Menurut Negara",
    #     zoom=2,
    #     center={"lat": -0.789275, "lon": 113.921327},  # Center map
    # )
    #
    # # Update layout for map style and controls
    # fig_country.update_layout(
    #     mapbox=dict(
    #         style="carto-darkmatter",
    #         center={"lat": -0.789275, "lon": 113.921327},
    #         zoom=2,
    #     ),
    #     margin={"r": 0, "t": 0, "l": 0, "b": 0},  # Adjust margins for clean fit
    # )
    #
    # # Display map in Streamlit
    # st.plotly_chart(fig_country, use_container_width=True)

    # Create a choropleth
    fig_country = px.choropleth(
        country_visits,
        locations='country',
        locationmode='country names',  # Directly use country names
        color='visit_count',
        hover_name='country',
        title=None,
        color_continuous_scale='Viridis',
        width=1200,
        height=800,
    )

    # Update geos for dark theme
    fig_country.update_geos(
        showcoastlines=False,
        # coastlinecolor="black",
        landcolor="#1a1a1a",  # Darker background color
        oceancolor="#2a2a2a",  # Dark grayish-blue ocean color
        showland=True,
        showocean=True,
        projection_scale=4,  # Scale for zoom effect
        center={"lat": -0.789275, "lon": 113.921327},  # Center the map
    )

    # Update layout for dark background
    # fig_country.update_layout(
    #     #paper_bgcolor="black",  # Background of the chart
    #     #plot_bgcolor="black",  # Background of the plot
    #     font=dict(color="white"),  # Font color
    #     title_font=dict(size=20, color="white"),  # Title font styling
    #     margin=dict(t=0, b=0, l=0, r=0)  # Remove all padding (set margins to 0)
    # )

    # Display map in Streamlit
    st.plotly_chart(fig_country, use_container_width=True, key=000)

    # Geographic Heatmap by City
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Kota")

    # Fill missing coordinates with placeholders if needed
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace with a meaningful default
    dfh['long'] = dfh['lon'].fillna(0)

    # make sure coordinate is numeric
    dfh['lat'] = pd.to_numeric(dfh['lat'], errors='coerce')
    dfh['lon'] = pd.to_numeric(dfh['lon'], errors='coerce')

    # Merge with city-level visit data and visualize
    city_visits = city_visits.merge(
        dfh[['city', 'lat', 'lon']].drop_duplicates(),
        on='city',
        how='left'
    )

    # Create scatter_mapbox
    fig_city = px.scatter_mapbox(
        city_visits,
        lat='lat',
        lon='lon',
        text='city',
        size='visit_count',
        color='visit_count',
        hover_name='city',
        color_continuous_scale='Tropic',
        width=1200,
        height=650,
    )

    # Update layout to center the map and show controls
    fig_city.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=-0.789275, lon=113.921327),  # Center map to specified lat/lon
            zoom=3.1,
        ),
        # margin={"r":0,"t":0,"l":0,"b":0},  # Optional: Adjust margins for better fit
        showlegend=True,  # Ensure legend is visible if applicable
    )

    # Show the map using Streamlit
    st.plotly_chart(fig_city, use_container_width=True,key=111)


#kunjungan per halaman
elif selected_tab == "Jumlah Kunjungan per Halaman":

    # DAILY TIME ANALYSYS
    st.markdown("### Analisa Kunjungan Per Hari Berdasarkan Negara dan Halaman")

    # Multiselect for countrycd
    selected_countries = st.multiselect(
        "Pilih Negara",
        options=["All"] + dfh['country'].unique().tolist(),
        default=["All"],
        key="halaman_country"
    )

    if "All" not in selected_countries:
        dfh = dfh[dfh['country'].isin(selected_countries)]

    # Multiselect for pages
    filtered_pages = dfh['title'].unique()
    selected_pages = st.multiselect(
        "Pilih Halaman",
        options=["All"] + sorted(filtered_pages),
        default=["All"],
    )

    if "All" not in selected_pages:
        dfh = dfh[dfh['title'].isin(selected_pages)]

    # Aggregate filtered data
    daily_visits_filtered = dfh.groupby('tanggal').size().reset_index(name='visit_count')

    # Plot filtered data
    if not daily_visits_filtered.empty:
        time_series_chart_filtered = alt.Chart(daily_visits_filtered).mark_line(point=True).encode(
            x=alt.X('tanggal:T', title='Tanggal'),
            y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
            tooltip=[
                alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
                alt.Tooltip('visit_count:Q', title='Kunjungan')
            ]
        ).properties(
            title="Kunjungan Per Hari Berdasarkan Halaman",
            height=400,
            width=1200
        ).interactive()
        st.altair_chart(time_series_chart_filtered)
    else:
        st.warning("Tidak ada  data tersedia untuk filters yang dipilih.")

    st.divider()


    st.markdown("## Kunjungan Per Halaman")
    # Altair Bar Chart

    # filter other or unknown
    df = dfh[~dfh['title'].isin(["Other", "Unknown", "Login", "Register"])]

    all_countries = df['country'].unique().tolist()

    selection = alt.selection_point(fields=['country'], bind='legend')

    bars = alt.Chart(df).mark_bar(size=6).encode(
        x=alt.X(
            "title:N",
            title="Judul Halaman",
            axis=alt.Axis(labelAngle=90),
            sort=alt.EncodingSortField(field="id", op="count", order="descending")
        ),
        y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
        xOffset=alt.X("country:N", title="Country"),  # Group by country
        color=alt.Color(
            "country:N",
            title="Negara",
            scale=alt.Scale(domain=all_countries),  # Explicitly set domain
            legend=alt.Legend(title="Pilih Negara")
        ),  # Different colors for each country
        tooltip=["country", "title", "count(id)"]  # Add tooltips for interactivity
    ).add_params(selection).transform_filter(selection).properties(
        height=800,
        width=1200
    ).interactive(bind_x=True, bind_y=True)

    st.altair_chart(bars)

    st.divider()

    df = df.copy()
    df['trunc_title'] = df['title'].apply(lambda x: x if len(x) <= 10 else x[:10] + '...')

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<h4 style='text-align: center;'>Top 10 Halaman/Menu</h4>", unsafe_allow_html=True)


        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = df['title'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = df[df['title'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_title:N",
                title=("Top 10 Halaman Dikunjungi"),
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["title", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)


    with colB:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Dalam Negri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is "Indonesia"
        indonesia_pages = df[df['country'] == 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = indonesia_pages['title'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = indonesia_pages[indonesia_pages['title'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_title:N",
                title="Judul Halaman",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=[ "title", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    with colC:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Luar Negeri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is outside "Indonesia"
        abroad_cities = df[df['country'] != 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = abroad_cities['title'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = abroad_cities[abroad_cities['title'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_title:N",
                title="Judul Halaman",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["title", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    st.divider()

    # still in tab1
    # Geographic Heatmap by Country
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Negara")

    # Aggregate visit data by country and city
    country_visits = dfh.groupby('country').size().reset_index(name='visit_count')
    city_visits = dfh.groupby(['country', 'city']).size().reset_index(name='visit_count')

    # Create a choropleth
    fig_country = px.choropleth(
        country_visits,
        locations='country',
        locationmode='country names',  # Directly use country names
        color='visit_count',
        hover_name='country',
        title=None,
        color_continuous_scale='Viridis',
        width=1200,
        height=800,
    )

    # Update geos for dark theme
    fig_country.update_geos(
        showcoastlines=False,
        # coastlinecolor="black",
        landcolor="#1a1a1a",  # Darker background color
        oceancolor="#2a2a2a",  # Dark grayish-blue ocean color
        showland=True,
        showocean=True,
        projection_scale=4,  # Scale for zoom effect
        center={"lat": -0.789275, "lon": 113.921327},  # Center the map
    )

    # Display map in Streamlit
    st.plotly_chart(fig_country, use_container_width=True, key=123)

    # Geographic Heatmap by City
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Kota")

    # Fill missing coordinates with placeholders if needed
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace with a meaningful default
    dfh['long'] = dfh['lon'].fillna(0)

    # make sure coordinate is numeric
    dfh['lat'] = pd.to_numeric(dfh['lat'], errors='coerce')
    dfh['lon'] = pd.to_numeric(dfh['lon'], errors='coerce')

    # Fill missing values
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace 0 with a meaningful default
    dfh['lon'] = dfh['lon'].fillna(0)

    # Calculate visit counts dynamically if not present
    # Create visit count by grouping on city and title
    dfh['visit_count'] = dfh.groupby(['city', 'title'])['title'].transform('count')

    # Add an "All Titles" option to the dropdown
    unique_titles = ['All'] + dfh['title'].unique().tolist()
    selected_title = st.selectbox("Pilih Halaman Yang Dikunjungi", options=unique_titles, index=0)

    # Filter data based on the selected title
    if selected_title == 'All':
        filtered_data = dfh.copy()  # Include all rows
    else:
        filtered_data = dfh[dfh['title'] == selected_title]  # Filter by specific title

    # Group the filtered data by city, lat, and lon to recalculate visit counts
    filtered_grouped = (
        filtered_data.groupby(['city', 'lat', 'lon'], as_index=False)
        .agg({'title': 'count'})  # Count the occurrences of the selected title
        .rename(columns={'title': 'visit_count'})  # Rename the column to visit_count
    )

    # Create scatter_mapbox
    fig_city = px.scatter_mapbox(
        filtered_grouped,
        lat='lat',
        lon='lon',
        size='visit_count',
        text='city',
        hover_name='city',
        hover_data={'visit_count': True, 'lat': False, 'lon': False},
        color='visit_count',  # Color represents visit count
        color_continuous_scale='Tropic',
        width=1200,
        height=650,
    )

    # Update layout
    fig_city.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=-0.789275, lon=113.921327),  # Center map
            zoom=3.1,
        ),
        showlegend=True
    )

    # Show map in Streamlit
    st.plotly_chart(fig_city, use_container_width=True,key=12345)

elif selected_tab == "Jumlah Kunjungan Halaman per Referensi Asal":
    #cross analysis page per utm source

    st.markdown("## Kunjungan ke Halaman per Referensi Asal")
    # Altair Bar Chart

    # filter other or unknown
    df = dfh[~dfh['title'].isin(["Other", "Unknown", "Login", "Register"])]

    # filter other or unknown
    df['utm_source'] = df['utm_source'].fillna('Other')

    all_utm = df['utm_source'].unique().tolist()

    selection = alt.selection_point(fields=['utm_source'], bind='legend')

    bars = alt.Chart(df).mark_bar(size=6).encode(
        x=alt.X(
            "title:N",
            title="Judul Halaman per Referensi Asal",
            axis=alt.Axis(labelAngle=90),
            sort=alt.EncodingSortField(field="id", op="count", order="descending")
        ),
        y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
        xOffset=alt.X("utm_source:N", title="Referensi Asal"),  # Group by country
        color=alt.Color(
            "utm_source:N",
            title="Referensi Asal",
            scale=alt.Scale(domain=all_utm),  # Explicitly set domain
            legend=alt.Legend(title="Pilih Referensi")
        ),  # Different colors for each country
        tooltip=["utm_source", "title", "count(id)"]  # Add tooltips for interactivity
    ).add_params(selection).transform_filter(selection).properties(
        height=800,
        width=1200
    ).interactive(bind_x=True, bind_y=True)

    st.altair_chart(bars)

elif selected_tab == "Jumlah Kunjungan Halaman per Tautan Asal":
    #cross analysis page per utm source

    st.markdown("## Kunjungan ke Halaman per Tautan Asal")
    # Altair Bar Chart

    # filter other or unknown
    df = dfh[~dfh['title'].isin(["Other", "Unknown", "Login", "Register"])]

    # filter other or unknown
    df['referrer'] = df['referrer'].fillna('Other')

    all_referrer = df['referrer'].unique().tolist()

    selection = alt.selection_point(fields=['utm_source'], bind='legend')

    bars = alt.Chart(df).mark_bar(size=6).encode(
        x=alt.X(
            "title:N",
            title="Judul Halaman per Tautan Asal",
            axis=alt.Axis(labelAngle=90),
            sort=alt.EncodingSortField(field="id", op="count", order="descending")
        ),
        y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
        xOffset=alt.X("utm_source:N", title="Tautan"),  # Group by country
        color=alt.Color(
            "utm_source:N",
            title="Tautan Asal",
            scale=alt.Scale(domain=all_referrer),  # Explicitly set domain
            legend=alt.Legend(title="Pilih Tautan Asal")
        ),  # Different colors for each country
        tooltip=["referrer", "title", "count(id)"]  # Add tooltips for interactivity
    ).add_params(selection).transform_filter(selection).properties(
        height=800,
        width=1200
    ).interactive(bind_x=True, bind_y=True)

    st.altair_chart(bars)

#kunjungan per link asal
elif selected_tab == "Jumlah Kunjungan per Referensi Asal":

    # DAILY TIME ANALYSYS
    st.markdown("### Analisa Kunjungan Per Hari Berdasarkan Referensi Asal dan Negara")

    # Multiselect for countrycd
    selected_countries = st.multiselect(
        "Pilih Negara",
        options=["All"] + dfh['country'].unique().tolist(),
        default=["All"],
        key="halaman_country1"
    )


    # filter other or unknown
    dfh['utm_source'] = dfh['utm_source'].fillna('Other')

    if "All" not in selected_countries:
        dfh = dfh[dfh['country'].isin(selected_countries)]

    # Multiselect for pages
    filtered_utms = dfh['utm_source'].unique()
    selected_utms = st.multiselect(
        "Pilih Referensi Asal",
        options=["All"] + sorted(filtered_utms),
        default=["All"],
    )

    if "All" not in selected_utms:
        dfh = dfh[dfh['utm_source'].isin(selected_utms)]

    # Aggregate filtered data
    daily_visits_filtered = dfh.groupby('tanggal').size().reset_index(name='visit_count')

    # Plot filtered data
    if not daily_visits_filtered.empty:
        time_series_chart_filtered = alt.Chart(daily_visits_filtered).mark_line(point=True).encode(
            x=alt.X('tanggal:T', title='Tanggal'),
            y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
            tooltip=[
                alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
                alt.Tooltip('visit_count:Q', title='Kunjungan')
            ]
        ).properties(
            title="Kunjungan Per Hari Berdasarkan Referensi Asal",
            height=400,
            width=1200
        ).interactive()
        st.altair_chart(time_series_chart_filtered)
    else:
        st.warning("Tidak ada  data tersedia untuk filters yang dipilih.")

    st.divider()


    st.markdown("## Kunjungan Per Referensi Asal")
    # Altair Bar Chart

    # filter other or unknown
    df['utm_source'] = df['utm_source'].fillna('Other')

    all_countries = df['country'].unique().tolist()

    selection = alt.selection_point(fields=['country'], bind='legend')

    bars = alt.Chart(df).mark_bar(size=6).encode(
        x=alt.X(
            "utm_source:N",
            title="Link Asal",
            axis=alt.Axis(labelAngle=90),
            sort=alt.EncodingSortField(field="id", op="count", order="descending")
        ),
        y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
        xOffset=alt.X("country:N", title="Country"),  # Group by country
        color=alt.Color(
            "country:N",
            title="Negara",
            scale=alt.Scale(domain=all_countries),  # Explicitly set domain
            legend=alt.Legend(title="Pilih Negara")
        ),  # Different colors for each country
        tooltip=["country", "utm_source", "count(id)"]  # Add tooltips for interactivity
    ).add_params(selection).transform_filter(selection).properties(
        height=800,
        width=1200
    ).interactive(bind_x=True, bind_y=True)

    st.altair_chart(bars)

    st.divider()

    df = df.copy()
    # filter other or unknown

    # filter other or unknown
    #df = dfh[~dfh['utm_source'].isin(["Unknown", None])]

    # Ensure all values in 'utm_source' are strings before applying the transformation
    df['utm_source'] = df['utm_source'].fillna('Other')
    df['trunc_utm_source'] = df['utm_source'].apply(lambda x: str(x) if len(str(x)) <= 10 else str(x)[:10] + '...')

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<h4 style='text-align: center;'>Top 10 Link Asal</h4>", unsafe_allow_html=True)


        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = df['utm_source'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = df[df['utm_source'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_utm_source:N",
                title=("Top 10 Referensi Asal Dikunjungi"),
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["utm_source", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)


    with colB:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Dalam Negri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is "Indonesia"
        indonesia_pages = df[df['country'] == 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = indonesia_pages['utm_source'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = indonesia_pages[indonesia_pages['utm_source'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_utm_source:N",
                title="Referensi Asal",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=[ "utm_source", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    with colC:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Luar Negeri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is outside "Indonesia"
        abroad_cities = df[df['country'] != 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = abroad_cities['utm_source'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = abroad_cities[abroad_cities['utm_source'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_utm_source:N",
                title="Referensi Asal",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["utm_source", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    st.divider()

    # still in tab1
    # Geographic Heatmap by Country
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Negara")

    # Aggregate visit data by country and city
    country_visits = dfh.groupby('country').size().reset_index(name='visit_count')
    city_visits = dfh.groupby(['country', 'city']).size().reset_index(name='visit_count')

    # Create a choropleth
    fig_country = px.choropleth(
        country_visits,
        locations='country',
        locationmode='country names',  # Directly use country names
        color='visit_count',
        hover_name='country',
        title=None,
        color_continuous_scale='Viridis',
        width=1200,
        height=800,
    )

    # Update geos for dark theme
    fig_country.update_geos(
        showcoastlines=False,
        # coastlinecolor="black",
        landcolor="#1a1a1a",  # Darker background color
        oceancolor="#2a2a2a",  # Dark grayish-blue ocean color
        showland=True,
        showocean=True,
        projection_scale=4,  # Scale for zoom effect
        center={"lat": -0.789275, "lon": 113.921327},  # Center the map
    )

    # Display map in Streamlit
    st.plotly_chart(fig_country, use_container_width=True, key=345)

    # Geographic Heatmap by City
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Kota")

    # Fill missing coordinates with placeholders if needed
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace with a meaningful default
    dfh['long'] = dfh['lon'].fillna(0)

    # make sure coordinate is numeric
    dfh['lat'] = pd.to_numeric(dfh['lat'], errors='coerce')
    dfh['lon'] = pd.to_numeric(dfh['lon'], errors='coerce')

    # Fill missing values
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace 0 with a meaningful default
    dfh['lon'] = dfh['lon'].fillna(0)

    # Calculate visit counts dynamically if not present
    # Create visit count by grouping on city and utm_source
    dfh['visit_count'] = dfh.groupby(['city', 'utm_source'])['utm_source'].transform('count')

    # Add an "All utm_sources" option to the dropdown
    unique_utm_sources = ['All'] + dfh['utm_source'].unique().tolist()
    selected_utm_source = st.selectbox("Pilih Referensi Asal Pengunjung", options=unique_utm_sources, index=0)

    # Filter data based on the selected utm_source
    if selected_utm_source == 'All':
        filtered_data = dfh.copy()  # Include all rows
    else:
        filtered_data = dfh[dfh['utm_source'] == selected_utm_source]  # Filter by specific utm_source

    # Group the filtered data by city, lat, and lon to recalculate visit counts
    filtered_grouped = (
        filtered_data.groupby(['city', 'lat', 'lon'], as_index=False)
        .agg({'utm_source': 'count'})  # Count the occurrences of the selected utm_source
        .rename(columns={'utm_source': 'visit_count'})  # Rename the column to visit_count
    )

    # Create scatter_mapbox
    fig_city = px.scatter_mapbox(
        filtered_grouped,
        lat='lat',
        lon='lon',
        size='visit_count',
        text='city',
        hover_name='city',
        hover_data={'visit_count': True, 'lat': False, 'lon': False},
        color='visit_count',  # Color represents visit count
        color_continuous_scale='Tropic',
        width=1200,
        height=650,
    )

    # Update layout
    fig_city.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=-0.789275, lon=113.921327),  # Center map
            zoom=3.1,
        ),
        showlegend=True
    )

    # Show map in Streamlit
    st.plotly_chart(fig_city, use_container_width=True,key=3456)

#kunjungan per link asal
elif selected_tab == "Jumlah Kunjungan per Tautan Asal":

    # DAILY TIME ANALYSYS
    st.markdown("### Analisa Kunjungan Per Hari Berdasarkan Tautan Asal dan Negara")

    # Multiselect for countrycd
    selected_countries = st.multiselect(
        "Pilih Negara",
        options=["All"] + dfh['country'].unique().tolist(),
        default=["All"],
        key="halaman_country2"
    )

    # Replace null/NaN values in the 'referrer' column with "other"
    dfh['referrer'] = dfh['referrer'].fillna('Other')

    if "All" not in selected_countries:
        dfh = dfh[dfh['country'].isin(selected_countries)]

    # filter other or unknown
    #dfh = dfh[~dfh['referrer'].isin([None])]

    # Multiselect for pages
    filtered_referrer = dfh['referrer'].unique()
    selected_referrers = st.multiselect(
        "Pilih Tautan",
        options=["All"] + sorted(filtered_referrer),
        default=["All"],
        key=222
    )

    if "All" not in selected_referrers:
        dfh = dfh[dfh['referrer'].isin(selected_referrers)]

    # Aggregate filtered data
    daily_visits_filtered = dfh.groupby('tanggal').size().reset_index(name='visit_count')

    # Plot filtered data
    if not daily_visits_filtered.empty:
        time_series_chart_filtered = alt.Chart(daily_visits_filtered).mark_line(point=True).encode(
            x=alt.X('tanggal:T', title='Tanggal'),
            y=alt.Y('visit_count:Q', title='Jumlah Kunjungan'),
            tooltip=[
                alt.Tooltip('tanggal:T', title='Tanggal', format='%Y-%m-%d'),
                alt.Tooltip('visit_count:Q', title='Kunjungan')
            ]
        ).properties(
            title="Kunjungan Per Hari Berdasarkan Tautan Asal",
            height=400,
            width=1200
        ).interactive()
        st.altair_chart(time_series_chart_filtered)
    else:
        st.warning("Tidak ada  data tersedia untuk filters yang dipilih.")

    st.divider()


    st.markdown("## Kunjungan Per Tautan Asal")
    # Altair Bar Chart

    # filter other or unknown
    df['referrer'] = df['referrer'].fillna('Other')

    all_countries = df['country'].unique().tolist()

    selection = alt.selection_point(fields=['country'], bind='legend')

    bars = alt.Chart(df).mark_bar(size=6).encode(
        x=alt.X(
            "referrer:N",
            title="Tautan Asal",
            axis=alt.Axis(labelAngle=90),
            sort=alt.EncodingSortField(field="id", op="count", order="descending")
        ),
        y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
        xOffset=alt.X("country:N", title="Country"),  # Group by country
        color=alt.Color(
            "country:N",
            title="Negara",
            scale=alt.Scale(domain=all_countries),  # Explicitly set domain
            legend=alt.Legend(title="Pilih Negara")
        ),  # Different colors for each country
        tooltip=["country", "referrer", "count(id)"]  # Add tooltips for interactivity
    ).add_params(selection).transform_filter(selection).properties(
        height=800,
        width=1200
    ).interactive(bind_x=True, bind_y=True)

    st.altair_chart(bars)

    st.divider()

    # filter other or unknown
    # df = dfh[~dfh['referrer'].isin([None])]
    df = df.copy()
    df['referrer'] = df['referrer'].fillna('Other')
    df['trunc_referrer'] = df['referrer'].apply(lambda x: str(x) if len(str(x)) <= 10 else str(x)[:10] + '...')

    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("<h4 style='text-align: center;'>Top 10 Tautan Asal</h4>", unsafe_allow_html=True)


        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = df['referrer'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = df[df['referrer'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_referrer:N",
                title=("Top 10 Tautan Asal"),
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["referrer", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)


    with colB:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Dalam Negri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is "Indonesia"
        indonesia_pages = df[df['country'] == 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = indonesia_pages['referrer'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = indonesia_pages[indonesia_pages['referrer'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_referrer:N",
                title="Tautan Asal",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=[ "referrer", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    with colC:
        st.markdown("<h4 style='text-align: center;'>Top 10 diakses Luar Negeri</h4>", unsafe_allow_html=True)

        # Filter rows where the country is outside "Indonesia"
        abroad_cities = df[df['country'] != 'Indonesia']

        # Select the top 10 cities (you can define criteria, e.g., most frequent)
        top_10_pages = abroad_cities['referrer'].value_counts().head(10).index.tolist()

        # Filter the DataFrame to include only these top 10 cities
        filtered_df = abroad_cities[abroad_cities['referrer'].isin(top_10_pages)]

        bars = alt.Chart(filtered_df).mark_bar(size=30).encode(
            x=alt.X(
                "trunc_referrer:N",
                title="Tautan Asal",
                axis=alt.Axis(labelAngle=90),
                sort=alt.EncodingSortField(field="id", op="count", order="descending")
            ),
            y=alt.Y("count(id):Q", title="Jumlah Kunjungan"),  # Count occurrences by city
            # Different colors for each country
            tooltip=["referrer", "count(id)"]  # Add tooltips for interactivity
        ).properties(
            height=400,
            width=400
        ).interactive(bind_x=True, bind_y=True)

        st.altair_chart(bars)

    st.divider()

    # still in tab1
    # Geographic Heatmap by Country
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Negara")

    # Aggregate visit data by country and city
    country_visits = dfh.groupby('country').size().reset_index(name='visit_count')
    city_visits = dfh.groupby(['country', 'city']).size().reset_index(name='visit_count')

    # Create a choropleth
    fig_country = px.choropleth(
        country_visits,
        locations='country',
        locationmode='country names',  # Directly use country names
        color='visit_count',
        hover_name='country',
        title=None,
        color_continuous_scale='Viridis',
        width=1200,
        height=800,
    )

    # Update geos for dark theme
    fig_country.update_geos(
        showcoastlines=False,
        # coastlinecolor="black",
        landcolor="#1a1a1a",  # Darker background color
        oceancolor="#2a2a2a",  # Dark grayish-blue ocean color
        showland=True,
        showocean=True,
        projection_scale=4,  # Scale for zoom effect
        center={"lat": -0.789275, "lon": 113.921327},  # Center the map
    )

    # Display map in Streamlit
    st.plotly_chart(fig_country, use_container_width=True, key=456)

    # Geographic Heatmap by City
    st.markdown("#### Trends Secara Geografis: Analisa Menurut Kota")

    # Fill missing coordinates with placeholders if needed
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace with a meaningful default
    dfh['long'] = dfh['lon'].fillna(0)

    # make sure coordinate is numeric
    dfh['lat'] = pd.to_numeric(dfh['lat'], errors='coerce')
    dfh['lon'] = pd.to_numeric(dfh['lon'], errors='coerce')

    # Fill missing values
    dfh['lat'] = dfh['lat'].fillna(0)  # Replace 0 with a meaningful default
    dfh['lon'] = dfh['lon'].fillna(0)

    # Calculate visit counts dynamically if not present
    # Create visit count by grouping on city and referrer
    dfh['visit_count'] = dfh.groupby(['city', 'referrer'])['referrer'].transform('count')

    # Add an "All referrers" option to the dropdown
    unique_referrers = ['All'] + dfh['referrer'].unique().tolist()
    selected_referrer = st.selectbox("Pilih Tautan Asal Pengunjung", options=unique_referrers, index=0, key="referrer2")

    # Filter data based on the selected referrer
    if selected_referrer == 'All':
        filtered_data = dfh.copy()  # Include all rows
    else:
        filtered_data = dfh[dfh['referrer'] == selected_referrer]  # Filter by specific referrer

    # Group the filtered data by city, lat, and lon to recalculate visit counts
    filtered_grouped = (
        filtered_data.groupby(['city', 'lat', 'lon'], as_index=False)
        .agg({'referrer': 'count'})  # Count the occurrences of the selected referrer
        .rename(columns={'referrer': 'visit_count'})  # Rename the column to visit_count
    )

    # Create scatter_mapbox
    fig_city = px.scatter_mapbox(
        filtered_grouped,
        lat='lat',
        lon='lon',
        size='visit_count',
        text='city',
        hover_name='city',
        hover_data={'visit_count': True, 'lat': False, 'lon': False},
        color='visit_count',  # Color represents visit count
        color_continuous_scale='Tropic',
        width=1200,
        height=650,
    )

    # Update layout
    fig_city.update_layout(
        mapbox=dict(
            style='carto-darkmatter',
            center=dict(lat=-0.789275, lon=113.921327),  # Center map
            zoom=3.1,
        ),
        showlegend=True
    )

    # Show map in Streamlit
    st.plotly_chart(fig_city, use_container_width=True,key=4567)


elif selected_tab == "Pengguna Terdaftar":

    interactive_table(dfu,
                      caption='Users',
                      select=False,
                      buttons=['copyHtml5', 'csvHtml5', 'excelHtml5', 'colvis'])