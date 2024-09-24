import streamlit as st
import rasterio
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import sqlite3
import tempfile
import matplotlib.pyplot as plt
import time
from datetime import datetime
from PIL import Image
from scipy.ndimage import label

st.set_page_config(layout='wide')

with st.sidebar:
    image_path = 'water_bodies_mapping/images/logo7.png'
    image = Image.open(image_path)
    with st.container(border=True):
        st.image(image, caption='Advanced Data Analytics and Predictive Technology', use_column_width=True)

# Function to read GeoTIFF and return the data, bounds, and metadata
def read_geotiff(file_path):
    with rasterio.open(file_path) as src:
        img_data = src.read(1)  # Read the first band
        bounds = src.bounds
        nodata = src.nodata
        metadata = src.meta  # Get metadata
        if nodata is not None:
            img_data = np.where(img_data == nodata, np.nan, img_data)  # Handle no data values
    return img_data, bounds, metadata

# Function to count water bodies
def count_water_bodies(img_data):
    threshold = 0.5  # Adjust this threshold based on your specific data
    binary_mask = img_data > threshold  # Create a binary mask for water bodies
    labeled_array, num_features = label(binary_mask)
    return num_features  # Return the number of detected water bodies

# Function to create heatmap
def create_heatmap(fig, img_data_normalized, bounds, selected_file):
    x = np.linspace(bounds.left, bounds.right, img_data_normalized.shape[1])
    y = np.linspace(bounds.bottom, bounds.top, img_data_normalized.shape[0])

    fig.add_trace(go.Heatmap(
        z=img_data_normalized,
        x=x,  # Longitude
        y=y,  # Latitude
        colorscale='Viridis',
        colorbar=dict(title='Normalized Value'),
        showscale=True,
    ))
    fig.update_layout(
        title=f'GeoTIFF Visualization: {selected_file}',
        xaxis_title='Longitude',
        yaxis_title='Latitude',
        xaxis=dict(scaleanchor="y"),
        yaxis=dict(constrain='domain'),
        yaxis_autorange='reversed',  # Reverse y-axis for true north
        mapbox=dict(
            style='carto-positron',
            center=dict(lon=(bounds.left + bounds.right) / 2, lat=(bounds.top + bounds.bottom) / 2),
            zoom=10,
        )
    )

# Water Body Analysis Page
def water_body_analysis():
    with st.container(border=False):
        st.markdown("<h1 style='text-align: center; color: #4B0082;'>🌊 ADAPT Water Body Analysis</h1>", unsafe_allow_html=True)

    folder_path = 'water_bodies_mapping/TIFF images'

    if os.path.isdir(folder_path):
        files = [f for f in os.listdir(folder_path) if f.endswith('.tif')]

        if files:
            with st.expander("📂 Click Here To Select GeoTIFF Files To View & Download"):
                selected_files = st.multiselect("Select GeoTIFF files:", files)

            if selected_files:
                num_files = len(selected_files)
                num_rows = (num_files + 1) // 2  # Calculate number of rows needed

                for row in range(num_rows):
                    col1, col2 = st.columns(2)

                    # First column
                    with col1:
                        if row * 2 < num_files:
                            selected_file = selected_files[row * 2]
                            file_path = os.path.join(folder_path, selected_file)
                            img_data, bounds, metadata = read_geotiff(file_path)

                            img_data_normalized = (img_data - np.nanmin(img_data)) / (np.nanmax(img_data) - np.nanmin(img_data))

                            fig1 = go.Figure()
                            create_heatmap(fig1, img_data_normalized, bounds, selected_file)
                            st.plotly_chart(fig1, use_container_width=True)

                            num_water_bodies = count_water_bodies(img_data_normalized)
                            st.write(f"👁️ Estimated Number of Water Bodies Detected: {num_water_bodies}")

                            st.subheader("📜 Metadata")
                            st.json(metadata)

                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download " + selected_file,
                                    data=f,
                                    file_name=selected_file,
                                    mime="image/tiff"
                                )

                    # Second column
                    with col2:
                        if row * 2 + 1 < num_files:
                            selected_file = selected_files[row * 2 + 1]
                            file_path = os.path.join(folder_path, selected_file)
                            img_data, bounds, metadata = read_geotiff(file_path)

                            img_data_normalized = (img_data - np.nanmin(img_data)) / (np.nanmax(img_data) - np.nanmin(img_data))

                            fig2 = go.Figure()
                            create_heatmap(fig2, img_data_normalized, bounds, selected_file)
                            st.plotly_chart(fig2, use_container_width=True)

                            num_water_bodies = count_water_bodies(img_data_normalized)
                            st.write(f"👁️ Estimated Number of Water Bodies Detected: {num_water_bodies}")

                            st.subheader("📜 Metadata")
                            st.json(metadata)

                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download " + selected_file,
                                    data=f,
                                    file_name=selected_file,
                                    mime="image/tiff"
                                )
                                
                                

            else:
                st.warning("⚠️ Please select at least one file to visualize.")
        else:
            st.warning("⚠️ No GeoTIFF files found in the specified folder.")
    else:
        st.warning("⚠️ The specified folder path is invalid.")

    st.divider()
    
    # Water Body Database Section
    with st.container(border=False):
        st.markdown("<h1 style='text-align: center; color: #4B0082;'>📊 ADAPT Water Body Database</h1>", unsafe_allow_html=True)

    df = pd.read_excel('bulawayo water bodies mapping project/datasets/2024 water body sizes.xlsx')

    with st.expander(label="📈 View Water Body Database, Graphs and Charts", expanded=False):
        col1, col2 = st.columns(2)

        water_body_names = df['water body name'].unique()
        with col1:
            selected_names = st.multiselect("Select Water Body Names To Start Analysis:", water_body_names)

        with col2:
            min_area, max_area = st.slider("Select Area Range (square meters):", 
                                             float(df['area (square meters)'].min()), 
                                             float(df['area (square meters)'].max()), 
                                             (float(df['area (square meters)'].min()), 
                                              float(df['area (square meters)'].max())))

        if selected_names:
            filtered_df = df[(df['water body name'].isin(selected_names)) & 
                             (df['area (square meters)'] >= min_area) & 
                             (df['area (square meters)'] <= max_area)]

            if filtered_df.empty:
                st.warning("⚠️ No water bodies found matching your criteria. Please adjust your filters.")
            else:
                col1, col2, col3 = st.columns([1, 5, 1])
                col1.empty()
                col2.dataframe(filtered_df)
                col3.empty()
                st.divider()

                fig1 = px.bar(filtered_df,
                              x='water body name',
                              y='area (square meters)',
                              hover_name='water body name',
                              hover_data='use/ purpose',
                              color='area (square meters)',
                              title='Filtered Bulawayo Water Bodies by Size and Usage Information')
                st.plotly_chart(fig1)
                st.divider()

                coz1, coz2 = st.columns([6, 2])
                fig2 = px.bar(filtered_df,
                               x='area (square meters)',
                               y='water body name',
                               hover_name='water body name',
                               hover_data='use/ purpose',
                               color='area (square meters)',
                               orientation='h',
                               title='Filtered Bulawayo Water Bodies Infographics Bar Chart')
                coz1.plotly_chart(fig2)

                fig3 = px.pie(filtered_df,
                               values='area (square meters)',
                               labels='water body name',
                               hover_name='water body name',
                               hover_data=['latitude', 'longitude'],
                               title='Filtered Bulawayo Water Bodies Infographics Pie Chart')
                coz2.plotly_chart(fig3)

        else:
            st.warning("⚠️ Please select at least one water body name to filter the data.")

    # Sidebar for FAQs and Contact
    with st.sidebar:
        st.title("❓ Frequently Asked Questions")
        with st.expander("❓ What services does Mthoe Saps Construction Technologies offer?"):
            st.write("""
                     Mthoe Saps Construction Technologies is a SaaS company based in Bulawayo, Zimbabwe that specializes in geospatial data analysis, remote sensing, and custom software development. We offer a range of services including:
                     - GIS and spatial data analysis 📊
                     - Remote sensing and satellite imagery processing 📡
                     - Streamlining workflows and processes through custom software development 🔗
                     - Providing software solutions for a variety of industries, not just construction
                     """)

        with st.expander("🏭 What industries do you serve?"):
            st.write("""
            While our roots are in the construction industry, we cater to clients across many different sectors, including:

            - Construction 🏗👷‍♂️
            - Real estate 🏨
            - Urban planning 🌆
            - Agriculture 🌾🐄
            - Mining ⛏
            - Environmental conservation 🏞
            - And more!
                     """)

        with st.expander("💼 How can I get started with your services?"):
            st.write("""
            To get started, you can reach out to us through one of our contact methods below. One of our representatives will be happy to discuss your specific needs and requirements, and provide more information about our capabilities and pricing.
            """)

        with st.expander("🛠️ What technologies do you use?"):
            st.write("""
            At the core of our solutions are Python data science libraries, which allow us to rapidly build and deploy custom web applications. We also leverage a variety of geospatial data tools and techniques, including remote sensing, GIS software, and spatial data analysis.
            """)

        with st.expander("🤝 Do you offer any support or training?"):
            st.write("""
            Absolutely. We understand that working with new technologies and software can be daunting, which is why we provide comprehensive support and training to all of our clients. This includes onboarding, documentation, and ongoing assistance to ensure you get the most out of our solutions.
            """)

        st.subheader("📞 Get in touch with us")
        selected_option = st.selectbox("Select Contact Method", ["WhatsApp", "LinkedIn", "Instagram"])
        if selected_option == "WhatsApp":
            st.info("Use the following buttons to get in touch with us:")
            st.markdown("[WhatsApp Us](https://wa.me/263777932721)")
        if selected_option == "LinkedIn":
            st.info("You can visit our LinkedIn profile and check our work, you can also contact us from there")
            st.markdown("[View our LinkedIn Profile](https://www.linkedin.com/in/mthokozisi-sapuwa-1ab2151ab?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app)")
        if selected_option == "Instagram":
            st.info("Find us on IG too")
            st.markdown("[Instagram Chat](https://www.instagram.com/mthoe_saps_construction_tech?igsh=MWZibnVpOWZkcmcyNg==)")

# Function for contributing maps
def contribute_map():
    # Define the upload folder path
    upload_folder = "water_bodies_mapping/map contributions"

    # Define the database path
    database_path = os.path.join(upload_folder, 'map_contributions.db')

    # Create or connect to the SQLite database
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Create a table if it doesn't exist (including email)
    c.execute('''
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY,
        map_name TEXT,
        contributor TEXT,
        email TEXT,
        timestamp TEXT,
        file_path TEXT
    )
    ''')
    conn.commit()

    # Streamlit app title
    with st.container(border=False):
        st.markdown("<h1 style='text-align: center; color: #4B0082;'>🗺️ ADAPT Map Contribution Upload</h1>", unsafe_allow_html=True)
    st.divider()

    # Create a row for input fields (Map Name, Contributor Name, and Email)
    col1, col2, col3 = st.columns(3)

    with col1:
        map_name = st.text_input("🗒️ Map Name")

    with col2:
        contributor = st.text_input("👤 Contributor Name")

    with col3:
        email = st.text_input("📧 Contributor Email")

    uploaded_file = st.file_uploader("📤 Choose a file to upload", type=["shp", "geojson", "dxf", "csv", "tif", "tiff"], label_visibility="collapsed")

    # Function to handle file upload
    def upload_map():
        if uploaded_file is not None:
            if map_name and contributor and email:
                # Save the uploaded file to the specified path with map name
                file_path = os.path.join(upload_folder, map_name)

                # Save the file with the appropriate extension
                file_extension = os.path.splitext(uploaded_file.name)[1]
                full_file_path = f"{file_path}{file_extension}"

                with open(full_file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
                # Insert record into the database
                timestamp = datetime.now().isoformat()
                c.execute('INSERT INTO contributions (map_name, contributor, email, timestamp, file_path) VALUES (?, ?, ?, ?, ?)',
                          (map_name, contributor, email, timestamp, full_file_path))
                conn.commit()

                # Success message with a warm thank you note
                st.success(f"🎉 Thank you for your contribution, {contributor}! Your file '{uploaded_file.name}' has been uploaded successfully as '{map_name}{file_extension}'.")
                st.info("ℹ️ Please note that your uploaded map will first be processed before it is made available for others to download and reuse.")
            else:
                st.warning("⚠️ Please enter all fields: Map Name, Contributor Name, and Contributor Email.")

    # Create a single row for the upload button and contributions select box
    col1, col2 = st.columns([2, 1])  # Adjusting column widths for better alignment

    with col1:
        if st.button("📥 Upload Map"):
            upload_map()

    with col2:
        c.execute('SELECT * FROM contributions')
        records = c.fetchall()
        contribution_options = [f"{row[1]} by {row[2]} on {row[3]}" for row in records]
        selected_contribution = st.selectbox("📜 Show Contributions", [""] + contribution_options)
        if selected_contribution:
            st.write(f"Selected Contribution: {selected_contribution}")

    # KPI Metrics
    c.execute('SELECT COUNT(*) FROM contributions')
    map_contributions_count = c.fetchone()[0]

    c.execute('SELECT MAX(timestamp) FROM contributions')
    last_upload_timestamp = c.fetchone()[0]

    # Custom CSS for styling the metrics and header
    st.markdown("""
    <style>
        .metric-container {
            display: flex;
            justify-content: space-between;
            margin-top: 20px;
        }
        .metric {
            flex: 1;
            text-align: center;
            margin: 0 10px;
            padding: 20px;
            border: 1px solid #e1e1e1;
            border-radius: 10px;
            background-color: #f9f9f9;
        }
    </style>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("<h1 style='text-align: center; color: #4B0082;'>📊 Contributions Key Performance Indicators</h1>", unsafe_allow_html=True)
    # Create a row for KPI metrics
    st.markdown('<div class="metric-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="metric"><h4>Total Map Contributions</h4><h2>{map_contributions_count}</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric"><h4>Last Upload</h4><h2>{last_upload_timestamp}</h2></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.divider()
        st.subheader('🔍 About Map Contribution', divider=True)
        st.sidebar.markdown("""
        ### 📜 Purpose
        The "Contribute Maps" section allows users to share their own maps of water bodies, enhancing our collective understanding and documentation of these vital resources.

        ### 🔍 Features
        - **👤 Contributor's Name**: Required field for identifying the individual who created the map.
        - **🗒️ Map Name**: Title of the map for easy reference and categorization.
        - **📧 Contributor's Email**: Contact information to facilitate communication regarding the map.
        - **📤 Upload Map**: A feature enabling users to upload their maps in various formats (e.g., PDF, PNG, JPEG).
        - **👁️ View Contributed Maps**: A section displaying all submitted maps along with the contributor's name and email.

        ### ✍️ How to Contribute
        1. Fill out the form with your name, email address, and the name of your map.
        2. Upload your map file using the designated upload button.
        3. Click "Submit" to share your contributions with the community.

        ### ⚖️ Guidelines
        - Ensure that the maps are accurate and represent water bodies correctly.
        - Respect the privacy of all contributors by not sharing their personal information without consent.

        ### 📬 Contact
        For any questions or concerns regarding map contributions, please contact us using the contact us section on the water bodies mapping page..
        """)

    # Close the database connection on app stop
    conn.close()

# Main function
def main():
    st.sidebar.title("📚 Navigation")
    page = st.sidebar.radio("Select a page:", ["🌊 Water Body Analysis", "🗺️ Contribute Your Map"])

    if page == "🌊 Water Body Analysis":
        water_body_analysis()
    elif page == "🗺️ Contribute Your Map":
        contribute_map()

if __name__ == "__main__":
    main()
