"""
Name: George Pav
CS230: Section SP22
Data: Pubs in England
URL: http://localhost:8501/
Description: This program reads a dataset which is titled (open_pubs_8000_sample.csv) and contains
a bunch of information about pubs in England. My code reads the data with the read_data() function.
After the data is written in I have coded a bunch of functions that are used to manipulate the data
and analyze them differently. My favorite line of code is the area chart where I used a list comprehension
to read and create the area chart.
"""

from collections import Counter
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Pubs in England",
    page_icon="🍻",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache
# reading in the data
def read_data():
    df = pd.read_csv("open_pubs_8000_sample.csv", index_col=0, header=[0], )
    df.ffill(axis=None, inplace=False, limit=None, downcast=None)
    df.latitude = pd.to_numeric(df.latitude)
    df.latitude = df.latitude.astype(float)
    return df


# filtering data so we can manipulate it
def filter_data(df, city):
    df = read_data()
    df_city = df[df['local_authority'] == city]
    return df_city


def create_map(df, size):
    map_df = df.filter(['name', 'latitude', 'longitude'])
    view_state = pdk.ViewState(latitude=map_df['latitude'].mean(), longitude=map_df['longitude'].mean(), zoom=6)
    pubs_layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_df,
        get_position='[longitude, latitude]',
        get_radius=size,
        get_color=[20, 175, 250],
        pickable=True)

    tool_tip = {'html': 'Listing:<br><b>{name}</b>', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}

    name = pdk.Deck(
        map_style='mapbox://styles/mapbox/outdoors-v11',
        initial_view_state=view_state,
        layers=[pubs_layer],
        tooltip=tool_tip
    )
    st.pydeck_chart(name)


def names_bar_chart(pubs, num, tick):
    plt.figure()
    plt.bar(tick, num, color=['yellow', 'green', 'purple'], edgecolor='blue')
    plt.xticks(tick, pubs, rotation=55)
    plt.xlabel("Pubs")
    plt.ylabel("Frequency")
    plt.xticks(rotation=55)
    plt.title("Popular Pubs and Their Frequency")

    return plt


def pie_chart(amt, picked_authorities):
    plt.figure()
    explodes = [0 for i in range(len(amt))]
    max = amt.index(np.max(amt))
    explodes[max] = 0.3
    plt.pie(amt, labels=picked_authorities, explode=explodes, autopct="%.5f")
    plt.title(f"Pub Frequency {', '.join(picked_authorities)}")

    return plt


# Creates an area chart of all the towns and pubs in England using a list comprehension
def area_chart(counts):
    chart_data = pd.counts([x for x in counts.values()], columns=[x for x in counts.keys()])

    return st.area_chart(chart_data)


# counts the number of occurrences of a name, uses the value counts method which finds all the occurrences of distinct
# strings in the df
def name_count(df):
    counts = df["local_authority"].value_counts()
    return counts

# creates a table based on what the user selects for the cities
def crawl_table(df, city):
    df = read_data()
    crawl = df.loc[df['local_authority'].isin(city)]
    return crawl


# uses zip to cycle through tuples with the counter function that is a dictionary subclass used for counting hashable
# objects
def common_names(df, counts):
    name, num = zip(*Counter(df['name']).most_common(counts))
    diff = np.arange(len(name))
    return name, num, diff


# simple function that returns all data for a selected local authority (or authorities)
def local_auth_filter(get_local_authority):
    df = read_data()
    df = df.loc[df['local_authority'].isin(get_local_authority)]

    return df

# counts the amount of local authorities in the data frame
def local_auth_counter(authorities, df):
    return [df.loc[df['local_authority'].isin([local_authority])].shape[0] for local_authority in authorities]

# returns a list that has all the local authorities
def all_local_authorities():
    list = []
    df = read_data()

    for c, r in df.iterrows():
        if r['local_authority'] not in list:
            list.append(r['local_authority'])

    return list


# sets up page basics
def main():
    st.sidebar.title("Directory")
    choices = st.sidebar.selectbox("Select a tab", ("Map", "Chart"))
    st.sidebar.markdown("***************")
    df = read_data()

    # if the user selects map then the code will show a map
    if choices == "Map":

        st.title("Pubs in England")
        st.subheader("Hopefully you are thirsty!")
        col1, col2, col3 = st.columns([1, 3, 1])
        with col1:
            st.write("")
        with col2:
            st.image("boris.jpeg", width=500)
        with col3:
            st.write("")
        # image from: https://www.politico.eu/article/boris-johnson-opens-the-pubs-in-england-as-corona-infections-fall/

        st.markdown("This is an interactive website created for users to view and analyze all of the pubs in england")
        st.sidebar.title("Follow the steps below to look at pubs in England")
        st.sidebar.markdown("***************")
        size = st.selectbox("Toggle point size", ([x for x in range(1000, 2000, 50)]))
        if size > 0:
            st.write("View a map of the pubs:")
            create_map(df, size)

        # User selects a city and clicks the button to add the city to their bar crawl
        city = [
            st.sidebar.selectbox(" 1.   Select a city, or type to find city", (df['local_authority']))]
        st.sidebar.markdown("***************")
        st.sidebar.markdown(" 2. Click the box below to view pubs in chosen city")
        st.sidebar.markdown("***************")
        click = st.sidebar.button("3.   Click to view pubs in city")

        if click:
            st.subheader("Your Selected pubs are shown below: ")
            result = crawl_table(df, city)
            st.write(result)

    # if the user selects chart then the code will show a chart and slider to select how many pubs per city
    if choices == "Chart":
        st.title("Pub frequency Analyzer")
        st.header("Bar Chart")
        amt = st.slider("Pick a number on the slider to display a bar chart ", 0, 50)
        st.write(f"You are viewing to view the top {amt} pub names")
        st.header("Pie Chart")
        st.write("Choose Local Authorities to see pub frequencies: ")
        authority = st.multiselect("Select a Local Authority: ", (df['local_authority']))
        data = local_auth_filter(authority)
        amount = local_auth_counter(authority, data)

        if len(authority) > 0:
            st.pyplot(pie_chart(amount, authority))
        data = read_data()
        if amt > 0:
            town_names, total, index = common_names(data, amt)
            st.pyplot(names_bar_chart(town_names, total, index))

        # area chart that shows all towns and pub frequencies, the user must click a checkbox to display it
        st.header("Area Chart")
        check = st.checkbox("Click to show Area Chart")
        if check:
            st.area_chart(name_count(df))

main()
