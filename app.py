import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium
from streamlit_folium import folium_static
from wordcloud import WordCloud
import seaborn as sns
from streamlit_extras.app_logo import add_logo
import streamlit.components.v1 as components


# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv('./data/flooddata.csv')
    return data

st.set_page_config(page_title="Flodd | Vizualization", page_icon=None, initial_sidebar_state="auto", menu_items=None)
st.set_option('deprecation.showPyplotGlobalUse', False)

df = load_data()


with st.sidebar:
  st.image("./img/logo.png", width=300)



def on_click(feature):
    st.session_state.selected_location = feature['properties']['Location']
    st.experimental_rerun()

# Sidebar for user input features
st.sidebar.header('Filter Options')

# Filter by Year
start_year, end_year = st.sidebar.slider('Select the year range', int(df['Year'].min()), int(df['Year'].max()), (int(df['Year'].min()), int(df['Year'].max())))
df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]

# Map Interaction and Filter by Location
st.session_state.selected_location = None

if 'Location' in df.columns:
    location = st.sidebar.text_input('Search for Location', st.session_state.selected_location if st.session_state.selected_location else "")
    if location:
        df_filtered = df_filtered[df_filtered['Location'].str.contains(location, case=False)]

# Filter by Main Cause
unique_causes = df['Main Cause'].unique()
selected_causes = st.sidebar.multiselect('Select Main Cause(s)', unique_causes, default=unique_causes)
df_filtered = df_filtered[df_filtered['Main Cause'].isin(selected_causes)]


st.header("FLODD: Unraveling India's Flood Odds")
st.write("Flodd provides a comprehensive analysis of flood events, utilizing a range of visualizations to explore patterns, trends, and impacts based on geographical data, temporal factors, and causal information. It is designed to aid researchers, policymakers, and the public in understanding the dynamics of floods and facilitating data-driven decision-making in disaster management and mitigation strategies.")

# Geo-spatial Visualization
st.header('Geo-spatial Visualization')
if not df_filtered.empty:
    map_data = df_filtered[['Latitude', 'Longitude', 'Location']]
    m = folium.Map(location=[map_data['Latitude'].mean(), map_data['Longitude'].mean()], zoom_start=5)
    for idx, row in map_data.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']], tooltip=row['Location'],
                      popup=row['Location']).add_to(m)
    folium_static(m)

# Counter Section with Scroll Triggered Animation
st.write("")
total_human_fatalities = int(df_filtered['Human fatality'].sum())
total_human_injuries = int(df_filtered['Human injured'].sum())
total_animal_fatalities = int(df_filtered['Animal Fatality'].sum())

counter_html = f"""
<div id="counter_section" style='display: flex; justify-content: space-around; align-items: center; text-align: center;'>
    <div>
        <h1 style="color: #ff6347;"><span id="human_fatalities">0</span></h1>
        <h4 style="color: #ffffff;">Human Fatalities</h4>
    </div>
    <div>
        <h1 style="color: #4682b4;"><span id="human_injuries">0</span></h1>
        <h4 style="color: #ffffff;">Human Injuries</h4>
    </div>
    <div>
        <h1 style="color: #3cb371;"><span id="animal_fatalities">0</span></h1>
        <h4 style="color: #ffffff;">Animal Fatalities</h4>
    </div>
</div>
<script>
document.addEventListener("DOMContentLoaded", function() {{
    const counterSection = document.getElementById('counter_section');
    let animated = false;  // Flag to ensure animation only plays once

    function animateValue(id, start, end, duration) {{
        let range = end - start;
        let current = start;
        let increment = (end > start) ? Math.ceil(range / (duration / 100)) : -Math.ceil(range / (duration / 100));
        let stepTime = Math.floor(duration / range);
        if (stepTime < 1) {{
            stepTime = 1;
        }}
        let obj = document.getElementById(id);
        let timer = setInterval(function() {{
            current += increment;
            if ((increment > 0 && current > end) || (increment < 0 && current < end)) {{
                current = end;
            }}
            obj.innerHTML = current;
            if (current == end) {{
                clearInterval(timer);
            }}
        }}, stepTime);
    }}

    function isInViewport() {{
        const rect = counterSection.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }}

    function checkAnimation() {{
        if (isInViewport() && !animated) {{
            animateValue("human_fatalities", 0, {total_human_fatalities}, 10000);
            animateValue("human_injuries", 0, {total_human_injuries}, 10000);
            animateValue("animal_fatalities", 0, {total_animal_fatalities}, 10000);
            animated = true;  // Set the flag so it won't animate again
        }}
    }}

    // Check on scroll and on load
    window.addEventListener('scroll', checkAnimation);
    checkAnimation();  // Also check when the page is loaded
}});
</script>
"""
components.html(counter_html, height=200)



# Time Series Analysis
st.header('Time Series Analysis')
if not df_filtered.empty:
    fig, ax = plt.subplots(figsize=(5, 3))
    df_filtered.groupby('Year').size().plot(ax=ax, title='Number of Flood Events Over Time')
    plt.xlabel('Year')
    plt.ylabel('Number of Events')
    st.pyplot(fig)

# Categorical Analysis
st.subheader('Cause(s) of Flood')
if not df_filtered.empty:
    fig, ax = plt.subplots(figsize=(5, 3))
    df_filtered['Main Cause'].value_counts().plot(kind='bar', ax=ax, title='Distribution of Main Causes of Floods')
    plt.xlabel('Main Cause')
    plt.ylabel('Frequency')
    st.pyplot(fig)

col1, col2 = st.columns(2)

with col1:
    st.subheader('Flood Duration')
    if not df_filtered.empty:
        fig, ax = plt.subplots(figsize=(5, 3))
        sns.histplot(df_filtered['Duration'], bins=20, kde=True, ax=ax)
        plt.title('Histogram of Flood Duration')
        st.pyplot(fig)

with col2:
    st.subheader('Fatalities and Injuries')
    if not df_filtered.empty:
        fig, ax = plt.subplots(figsize=(5, 3.25))
        sns.boxplot(data=df_filtered[['Human fatality', 'Human injured', 'Animal Fatality']], ax=ax)
        plt.title('Boxplot for Fatalities and Injuries')
        st.pyplot(fig)

st.subheader('Humans Injured')
if not df_filtered.empty:
    fig, ax = plt.subplots(figsize=(5, 3))
    sns.scatterplot(data=df_filtered, x='Duration', y='Human injured', ax=ax)
    plt.title('Duration vs. Human Injured')
    st.pyplot(fig)

# Statistical and Word Cloud Analysis below the columns
st.subheader('Loss of Life')
if not df_filtered.empty:
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(df_filtered[['Duration', 'Human fatality', 'Animal Fatality']].corr(), annot=True, ax=ax)
    st.pyplot(fig)

st.subheader('What exactly Happened?')
try:
    if not df_filtered.empty:
        text = ' '.join(df_filtered['Details'].dropna())
        wordcloud = WordCloud(width=800, height=400).generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud)
        plt.axis("off")
        st.pyplot()
except KeyError:
    st.error("No Details Found!")
except Exception as e:
    st.error(f"Error: {e}")

