import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static
from folium.plugins import HeatMap

# Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("vehicles.csv")
        df = df.dropna(subset=["manufacturer", "model", "year", "price", "lat", "long", "cylinders", "fuel", "drive"])
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df = pd.DataFrame()
    return df

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Home", 
    "Models by Company",
    "Most Listed Vehicle Brands", 
    "Transmission vs Type", 
    "Manufacturer vs Drive", 
    "Brand-Specific Heatmap"
])

# Load data
df = load_data()

# Pages
if page == "Home":
    st.title("🚗 Used Vehicle Market Analysis Dashboard")
    st.markdown("---")
    st.markdown("### Welcome! ")
    st.markdown("""
    Dive into insights from the used vehicle market across the US.  
    This dashboard lets you **explore car listings** with interactive maps, charts, and filters.

    **Here's what you can do:**
    -  Browse car models by manufacturer  
    -  See top-listed brands & transmission types  
    -  Explore regional trends with heatmaps  
    -  Discover car specs like fuel type, drive, and price range  
    """)
    
    st.markdown("---")
    st.markdown("### Dataset Preview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Listings", f"{len(df):,}")
    with col2:
        st.metric("Unique Brands", df['manufacturer'].nunique())
    with col3:
        st.metric("Unique Models", df['model'].nunique())

    st.markdown("""---""")

elif page == "Models by Company":
    st.subheader(" Models by Manufacturer")

    if not df.empty and {'manufacturer', 'model', 'price', 'drive', 'type', 'transmission', 'year', 'fuel', 'cylinders'}.issubset(df.columns):
        selected_brand = st.selectbox("Choose a Company:", sorted(df['manufacturer'].dropna().unique()))
        brand_df = df[df['manufacturer'] == selected_brand].dropna(subset=['model'])

        search_query = st.text_input("Search for a specific model (optional):").lower()

        if not brand_df.empty:
            if search_query:
                brand_df = brand_df[brand_df['model'].str.lower().str.contains(search_query)]

            if not brand_df.empty:
                grouped = brand_df.groupby('model').agg({
                    'price': 'mean',
                    'drive': lambda x: x.mode().iat[0] if not x.mode().empty else 'N/A',
                    'type': lambda x: x.mode().iat[0] if not x.mode().empty else 'N/A',
                    'transmission': lambda x: x.mode().iat[0] if not x.mode().empty else 'N/A',
                    'fuel': lambda x: x.mode().iat[0] if not x.mode().empty else 'N/A',
                    'cylinders': lambda x: x.mode().iat[0] if not x.mode().empty else 'N/A',
                    'year': lambda x: int(x.median()) if not x.isnull().all() else 'N/A'
                }).reset_index()

                for _, row in grouped.iterrows():
                    st.markdown(f"""
                    **Model:** {row['model']}  
                    - Average Price: ${row['price']:.2f}  
                    - Year (Median): {row['year']}  
                    - Drive: {row['drive']}  
                    - Type: {row['type']}  
                    - Transmission: {row['transmission']}  
                    - Fuel: {row['fuel']}  
                    - Cylinders: {row['cylinders']}  
                    """)
            else:
                st.warning("No matching models found.")
        else:
            st.warning("No models found for this company.")
    else:
        st.warning("Required columns are missing from the dataset.")

elif page == "Most Listed Vehicle Brands":
    st.subheader("Most Listed Vehicle Brands")
    if not df.empty and 'manufacturer' in df.columns:
        manufacturer_counts = df.manufacturer.value_counts().nlargest(10)
        fig_manu = px.pie(
            names=manufacturer_counts.index,
            values=manufacturer_counts.values,
            title="Top 10 Manufacturers"
        )
        st.plotly_chart(fig_manu)
    else:
        st.warning("No data or 'manufacturer' column missing.")

elif page == "Transmission vs Type":
    st.subheader("Transmission vs Type")
    if not df.empty:
        fig_trans_type = px.histogram(df, x="transmission", color="type", 
                                      title="Transmission vs Type", barmode="group")
        st.plotly_chart(fig_trans_type)
    else:
        st.warning("Data not loaded.")

elif page == "Manufacturer vs Drive":
    st.subheader("Manufacturer vs Drive")
    if not df.empty:
        fig_manufacturer_drive = px.bar(df, x="manufacturer", color="drive", 
                                        title="Manufacturer vs Drive", barmode="group")
        st.plotly_chart(fig_manufacturer_drive)
    else:
        st.warning("Data not loaded.")

elif page == "Brand-Specific Heatmap":
    st.subheader(" Heatmap of Selected Brand")
    if not df.empty and {'manufacturer', 'lat', 'long'}.issubset(df.columns):
        selected_brand = st.selectbox("Select a Manufacturer:", sorted(df['manufacturer'].dropna().unique()))
        brand_df = df[df['manufacturer'] == selected_brand]

        if not brand_df.empty:
            map_brand_specific = folium.Map(location=[brand_df['lat'].mean(), brand_df['long'].mean()], zoom_start=5)
            heat_data = [[row['lat'], row['long']] for _, row in brand_df.iterrows()]
            HeatMap(heat_data, min_opacity=0.3, radius=15, blur=10).add_to(map_brand_specific)
            folium_static(map_brand_specific)
        else:
            st.warning("No data available for this manufacturer.")
    else:
        st.warning("Required columns ('manufacturer', 'lat', 'long') not found in dataset.")

