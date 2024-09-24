import streamlit as st
import os
import sqlite3
import pandas as pd
import plotly.express as px
import base64
from datetime import datetime
from PIL import Image

# Set the page configuration
st.set_page_config(layout='wide', page_title="ADAPT - Advanced Data Analytics", page_icon="📊")

with st.sidebar:
    image_path = 'c:/Users/mthoe/OneDrive/Desktop/bulawayo water bodies mapping project/images/logo7.png'
    image = Image.open(image_path)
    with st.container(border=True):
        st.image(image, caption='Advanced Data Analytics and Predictive Technology', use_column_width=True)

# Define the folder paths
upload_folder = 'c:/Users/mthoe/OneDrive/Desktop/bulawayo water bodies mapping project/TIFF images'
excel_folder = 'c:/Users/mthoe/OneDrive/Desktop/bulawayo water bodies mapping project/datasets'
database_path = os.path.join(upload_folder, 'map_contributions.db')
map_contributions_folder = 'c:/Users/mthoe/OneDrive/Desktop/bulawayo water bodies mapping project/map contributions'

# Function to initialize the database and create the contributions table
def init_database():
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
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
    conn.close()

# Function to display info icon with tooltip
def info_icon(message):
    return f'<span style="cursor: pointer; float: right; margin-left: 10px;" title="{message}">ℹ️</span>'

# Admin Panel Function
def admin_panel():
    st.markdown("<h1 style='text-align: center; color: #4B0082;'>ADAPT: Advanced Data Analytics & Predictive Technology</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #4B0082;'>🗂️ Admin Panel: Upload GeoTIFF Files" + info_icon("Supported file formats for upload: GeoTIFF files (.tif, .tiff), Shapefiles (.shp), DXF files (.dxf), Image files (.png, .jpg, .jpeg)") + "</h2>", unsafe_allow_html=True)
    st.divider()

    # File uploader for GeoTIFF files
    uploaded_file = st.file_uploader("📤 Choose a GeoTIFF file to upload", type=["tif", "tiff"])

    # Function to handle GeoTIFF file upload
    def upload_geotiff():
        if uploaded_file is not None:
            file_path = os.path.join(upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            timestamp = datetime.now().isoformat()
            st.success(f"🎉 Successfully uploaded '{uploaded_file.name}' to '{upload_folder}' on {timestamp}.")
            log_contribution(uploaded_file.name, timestamp)

    # Log the contribution in the database
    def log_contribution(file_name, timestamp):
        conn = sqlite3.connect(database_path)
        c = conn.cursor()
        c.execute('INSERT INTO contributions (map_name, contributor, email, timestamp, file_path) VALUES (?, ?, ?, ?, ?)',
                  (file_name, "Admin", "admin@example.com", timestamp, os.path.join(upload_folder, file_name)))
        conn.commit()
        conn.close()

    # Create an upload button for GeoTIFF
    if st.button("📥 Upload GeoTIFF"):
        upload_geotiff()

    # Header for Uploaded Files
    st.markdown("<h2 style='color: #4B0082;'>📂 View Uploaded Files" + info_icon("Supported formats: GeoTIFF files (.tif, .tiff), Shapefiles (.shp), DXF files (.dxf), Image files (.png, .jpg, .jpeg)") + "</h2>", unsafe_allow_html=True)
    
    # Display Uploaded Files with Search
    with st.expander("Click to view uploaded files", expanded=False):
        list_uploaded_files()

    # View Map Contributions Section Header
    st.markdown("<h2 style='color: #4B0082;'>🗺️ View Map Contributions" + info_icon("Supported formats: GeoTIFF files (.tif, .tiff), Shapefiles (.shp), DXF files (.dxf), Image files (.png, .jpg, .jpeg)") + "</h2>", unsafe_allow_html=True)
    
    with st.expander("Details", expanded=False):
        view_map_contributions()

    # Excel File Upload Section
    st.divider()
    st.markdown("<h2 style='color: #4B0082;'>📊 Manage Excel Database" + info_icon("Supported format: Excel files (.xlsx)") + "</h2>", unsafe_allow_html=True)

    # List existing Excel files
    existing_excel_files = [f for f in os.listdir(excel_folder) if f.endswith('.xlsx')]
    if existing_excel_files:
        # Select box for current Excel files
        selected_file = st.selectbox("📝 Select an Excel file to delete:", existing_excel_files)

        # Delete selected file
        if st.button("🗑️ Delete Selected Excel File"):
            os.remove(os.path.join(excel_folder, selected_file))
            st.success(f"🎉 Successfully deleted '{selected_file}'.")

    # Input field for new Excel file name
    new_excel_file_name = st.text_input("📝 Enter new Excel file name (without extension):", "")
    excel_file = st.file_uploader("📤 Upload new Excel database", type=["xlsx"])

    # Function to replace the existing Excel database
    def replace_excel_database():
        if excel_file is not None and new_excel_file_name:
            new_file_path = os.path.join(excel_folder, new_excel_file_name + ".xlsx")
            with open(new_file_path, "wb") as f:
                f.write(excel_file.getbuffer())
            st.success(f"🎉 Successfully replaced the Excel database with '{new_excel_file_name}.xlsx'.")

    # Create a button to replace the Excel database
    if st.button("🔄 Replace Excel Database"):
        replace_excel_database()

def list_uploaded_files():
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = os.listdir(upload_folder)

    files = st.session_state.uploaded_files
    
    # Search Bar
    search_query = st.text_input("🔍 Search by file name:", "")
    
    # Filtered Files
    filtered_files = files
    if search_query:
        filtered_files = [file for file in files if search_query.lower() in file.lower()]
    
    if filtered_files:
        for file in filtered_files:
            file_path = os.path.join(upload_folder, file)
            file_size = os.path.getsize(file_path)  # Get file size in bytes
            upload_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

            st.write(file)
            st.write(f"**Size**: {file_size / 1024:.2f} KB | **Uploaded On**: {upload_time}")

            delete_button = st.button(f"🗑️ Delete {file}", key=file)
            if delete_button:
                os.remove(file_path)
                st.session_state.uploaded_files.remove(file)  # Remove from session state
                st.success(f"🎉 '{file}' has been deleted.")
                break  # Exit the loop to refresh the display
    else:
        st.warning("⚠️ No files match your search criteria.")

def view_map_contributions():
    map_files = [f for f in os.listdir(map_contributions_folder) if f.endswith(('.tif', '.tiff', '.shp', '.dxf', '.png', '.jpg', '.jpeg'))]
    
    if map_files:
        for map_file in map_files:
            file_path = os.path.join(map_contributions_folder, map_file)
            file_size = os.path.getsize(file_path)  # Get file size in bytes
            upload_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

            st.write(map_file)
            st.write(f"**Size**: {file_size / 1024:.2f} KB | **Uploaded On**: {upload_time}")

            # Display the map image if it's a supported format
            if map_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                st.image(file_path, use_column_width=True)
            else:
                st.write(f"Viewing {map_file} is not supported directly. Download it [here]({file_path}).")

            col1, col2 = st.columns([3, 1])
            with col1:
                # Use HTML to create a styled download button
                st.markdown(f"""
                    <a href="data:file/octet-stream;base64,{get_file_data(file_path)}" download="{map_file}" 
                       style="display:inline-block; background-color:#4B0082; color:white; padding:10px 20px; 
                       border-radius:5px; text-decoration:none; transition: background-color 0.3s;">
                       📥 Download {map_file}
                    </a>
                """, unsafe_allow_html=True)

            with col2:
                # Use a simple button for delete
                if st.button(f"🗑️ Delete {map_file}", key=f"delete_{map_file}"):
                    os.remove(file_path)
                    st.success(f"🎉 '{map_file}' has been deleted.")
                    break  # Exit the loop to refresh the display
    else:
        st.warning("⚠️ No map contributions found.")

def get_file_data(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# KPI Metrics Page Function
def kpi_metrics_page():
    st.markdown("<h1 style='text-align: center; color: #4B0082;'>ADAPT: Advanced Data Analytics & Predictive Technology</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #4B0082;'>📊 KPI Metrics</h2>", unsafe_allow_html=True)
    st.divider()

    # Connect to the database and fetch metrics
    conn = sqlite3.connect(database_path)
    c = conn.cursor()

    # Fetch total contributions
    c.execute('SELECT COUNT(*) FROM contributions')
    total_contributions = c.fetchone()[0]

    # Fetch the latest upload timestamp
    c.execute('SELECT MAX(timestamp) FROM contributions')
    last_upload_timestamp = c.fetchone()[0]

    # Fetch total file size over time with file names
    c.execute('SELECT timestamp, SUM(LENGTH(file_path)), GROUP_CONCAT(map_name) FROM contributions GROUP BY timestamp ORDER BY timestamp')
    size_over_time = c.fetchall()

    # Close the database connection
    conn.close()

    # Convert the data into a DataFrame for plotting
    df_size = pd.DataFrame(size_over_time, columns=['timestamp', 'total_size', 'file_names'])
    df_size['timestamp'] = pd.to_datetime(df_size['timestamp'])
    
    # Display the metrics in a nice format using columns
    col1, col2 = st.columns(2)

    # Custom CSS for metric cards
    st.markdown("""
        <style>
        .metric-card {
            background-color: #f9f9f9;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        .metric-value {
            font-size: 2em;
            color: #4B0082;
        }
        .metric-label {
            font-size: 1.2em;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Map Contributions</div>
                <div class="metric-value">{total_contributions}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        last_upload_display = last_upload_timestamp if last_upload_timestamp else "No uploads yet"
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Last Upload Timestamp</div>
                <div class="metric-value">{last_upload_display}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Plot Total Size Over Time
    st.subheader("📈 Total Size of Contributions Over Time")
    fig = px.line(df_size, x='timestamp', y='total_size', title='Total Size of Contributions Over Time (in bytes)', markers=True)

    # Update hover data to include file names
    fig.update_traces(hovertemplate='Date: %{x}<br>Total Size: %{y} bytes<br>Files: %{customdata}<extra></extra>', 
                      customdata=df_size['file_names'])

    st.plotly_chart(fig)

    # Display the Excel DataFrame
    st.divider()
    st.markdown("<h2 style='color: #4B0082;'>📊 Water Body Sizes Data</h2>", unsafe_allow_html=True)

    # List existing Excel files and select one to display
    existing_excel_files = [f for f in os.listdir(excel_folder) if f.endswith('.xlsx')]
    if existing_excel_files:
        selected_excel_file = st.selectbox("📝 Select an Excel file to display:", existing_excel_files)

        # Load and display the selected Excel data
        try:
            excel_file_path = os.path.join(excel_folder, selected_excel_file)
            df_water_body_sizes = pd.read_excel(excel_file_path)
            st.dataframe(df_water_body_sizes)
        except Exception as e:
            st.error(f"⚠️ Error loading Excel file: {e}")
    else:
        st.warning("⚠️ No Excel files found in the directory.")

# Main function
def main():
    init_database()  # Initialize the database
    st.sidebar.title("📚 ADAPT Admin Navigation")
    
    # Navigation Links
    page = st.sidebar.radio("🔄 Select a page:", ["🗂️ Admin Panel", "📊 KPI Metrics"])
    
    # Project Description
    st.sidebar.markdown("""
        ### 🌊 Project Overview
        **ADAPT** (Advanced Data Analytics & Predictive Technology) is designed to help manage and analyze mapping data for water bodies in Bulawayo.
        
        This application allows users to upload, manage, and visualize GeoTIFF files and Excel datasets related to water bodies.
    """)

    # Links to Resources
    st.sidebar.markdown("### 🔗 Useful Links")
    st.sidebar.markdown("""
        - 📖 [Documentation](https://example.com/documentation)  
        - 🐱‍💻 [GitHub Repository](https://github.com/your-repo)
        - 📧 [Contact Support](mailto:support@example.com)
    """)

    # Current User Information (optional)
    st.sidebar.markdown("### 👤 Current User")
    st.sidebar.markdown("**Admin**")

    if page == "🗂️ Admin Panel":
        admin_panel()
    elif page == "📊 KPI Metrics":
        kpi_metrics_page()

if __name__ == "__main__":
    main()
