import pandas as pd
import requests
import csv
import streamlit as st
from streamlit_extras.stylable_container import stylable_container

@st.cache_resource

# API URL


def fetch_data_user(urluser):
    response = requests.get(urluser)
    data = response.json()
    return pd.DataFrame(data)

def fetch_data_hit(urlhit):
    response = requests.get(urlhit)
    data = response.json()
    return pd.DataFrame(data)

def users_csv(file_csv):
    import requests
    import csv

    # API URL
    url = "https://restful.abangadek-adv.com/users"

    # Optional: Include headers or parameters
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }

    # GET request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Parse JSON response

        # Filepath for CSV
        csv_file = file_csv

        # Write JSON data to CSV
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Assuming data is a list of dictionaries
            if isinstance(data, list) and len(data) > 0:
                # Write header row
                writer.writerow(data[0].keys())
                # Write data rows
                for row in data:
                    writer.writerow(row.values())

            print(f"Data successfully written to {csv_file}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def hits_csv(file_csv):
    import requests
    import csv

    # API URL
    url = "https://restful.abangadek-adv.com/hits"

    # Optional: Include headers or parameters
    headers = {
        "Authorization": "Bearer YOUR_ACCESS_TOKEN",
        "Content-Type": "application/json"
    }

    # GET request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()  # Parse JSON response

        # Filepath for CSV
        csv_file = file_csv

        # Write JSON data to CSV
        with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Assuming data is a list of dictionaries
            if isinstance(data, list) and len(data) > 0:
                # Write header row
                writer.writerow(data[0].keys())
                # Write data rows
                for row in data:
                    writer.writerow(row.values())

            print(f"Data successfully written to {csv_file}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")



def load_users(csv_file):
    dfu= pd.read_csv(csv_file)
    return dfu

def load_hits(csv_file):
    dfh= pd.read_csv(csv_file)
    return dfh


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
    if wilayah == "Brand Outlets Branch":
        return pd.read_csv('dataoutlet.csv'), [
            {"text": "2142", "lat": -3.47, "lon": 105.96, "radius": 6000}], 8, 0.5072459760797242, 101.44711771077857
    elif wilayah == "Brand Outlets Subdist":
        return pd.read_csv('dataoutlet.csv'), [
            {"text": "15848", "lat": -3.47, "lon": 106.139, "radius": 12000}], 7, 0.5072459760797242, 101.44711771077857
    elif wilayah == "Indonesia":
        return pd.read_csv('dataoutlet.csv'), [
            {"text": "6194", "lat": -4, "lon": 117.5, "radius": 85000}], 3.7, -4, 117.5


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