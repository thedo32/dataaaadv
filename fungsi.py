import pandas as pd
import geopy.distance
import csv
import geojson
import streamlit as st

from streamlit_extras.stylable_container import stylable_container

@st.cache_resource

def addDistance (inputPath,outputPath) :
    dfloc = pd.read_csv(inputPath)


    for i in range(len(dfloc)):
        coords_1 = (dfloc.loc[i, "latitude"], dfloc.loc[i, "longitude"])
        coords_2 = (dfloc.loc[i, "lat_pol"], dfloc.loc[i, "lon_pol"])
        distance = geopy.distance.geodesic(coords_1, coords_2).km
        print(distance)
        df = pd.DataFrame({distance})
        df.to_csv(outputPath, mode="a", index=False, header=False)

def csv_to_geojson(csv_file, geojson_file):
    features = []
    with open(csv_file, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            # Assuming your CSV has 'latitude' and 'longitude' columns
            latitude = float(row['latitude'])
            longitude = float(row['longitude'])

            feature = geojson.Feature(
                geometry=geojson.Point((longitude, latitude)),
                properties=row
            )
            features.append(feature)

    feature_collection = geojson.FeatureCollection(features)

    with open(geojson_file, 'w') as f:
        geojson.dump(feature_collection, f, indent=2)

def format_big_number(num):
    if num >= 1e6:
        return f"{num / 1e6:.1f} Mio"
    elif num >= 1e3:
        return f"{num / 1e3:.1f} K"
    elif num >= 1e2:
        return f"{num / 1e3:.1f} K"
    else:
        return f"{num:.2f}"

def wilayah_admin(wilayah):
    if wilayah == 25:
        df1 = pd.read_csv('maps/palembang25.csv')
        bubbletext = [{"text": "438", "lat": -3.47, "lon": 105.96}]
    elif wilayah == 50:
        df1 = pd.read_csv('maps/palembang50.csv')
        bubbletext = [{"text": "2142", "lat": -3.47, "lon": 105.96}]
    elif wilayah == 75:
        df1 = pd.read_csv('maps/palembang75.csv')
        bubbletext = [{"text": "6194", "lat": -3.47, "lon": 105.96}]
    elif wilayah == "Sumsel":
        df1 = pd.read_csv('maps/sumsel.csv')
        bubbletext = [{"text": "6194", "lat": -3.47, "lon": 106.139}]
    else:
        df2 = pd.read_csv('maps/sumsel.csv')
        bubbletext = [{"text": "15848", "lat": -3.47, "lon": 106.139}]


def stylebutton(textcontain):
    with stylable_container(
        key="green_button",
        css_styles="""
            button {
                background-color: green;
                color: white;
                border-radius: 20px;
            }
            """,
    ):
        st.button(textcontain, unsafe_allow_html=True)

def stylecapt(textcontain):
    with stylable_container(
            key="container_with_border",
            css_styles="""
              {
                  border: 2px solid rgba(49, 51, 63, 0.2);
                  border-radius: 0.5rem;
                  background-color: rgba(100, 76, 76, 0.2);
                  padding: calc(1em - 1px)
              }
              """,
    ):
        st.caption(textcontain, unsafe_allow_html=True)

def stylemd(textcontain):
    with stylable_container(
            key="container_with_border",
            css_styles="""
              {
                  border: 2px solid rgba(49, 51, 63, 0.2);
                  border-radius: 0.5rem;
                  background-color: rgba(100, 76, 76, 0.2);
                  padding: calc(1em - 1px)
              }
              """,
    ):
        st.markdown(textcontain, unsafe_allow_html=True)






