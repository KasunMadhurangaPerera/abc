import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection parameters
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'VALUATION'

# Custom CSS to reduce font size for metrics
st.markdown(
    """
    <style>
    [data-testid="stMetricValue"] {
        font-size: 20px !important; /* Adjust font size here */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Connect to the MySQL database
@st.cache_data
def get_data_from_db():
    engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    query = "SELECT * FROM vehicles"  # Replace with your actual table name
    data = pd.read_sql(query, con=engine)
    return data

# Load data
data = get_data_from_db()

# Ensure 'year_month' column exists and is in the format "YY/MM"
if 'year_month' not in data.columns:
    if 'yymm' in data.columns:  # Assuming 'yymm' exists
        data['year_month'] = data['yymm'].astype(str).str[:2] + "/" + data['yymm'].astype(str).str[2:]
    else:
        st.error("The 'year_month' or 'yymm' column is missing from the dataset.")
        st.stop()

# Sidebar Filters with unique keys
st.sidebar.header("Filters")

# Filter for Make (Brand)
brand = st.sidebar.selectbox(
    "Select Make (Brand)", 
    options=["All"] + list(data['brand'].unique()),
    key="brand_filter"  # Unique key
)

# Filter for Model
model = st.sidebar.selectbox(
    "Select Model", 
    options=["All"] + list(data['model'].unique()),
    key="model_filter"  # Unique key
)

# Filter for Year of Manufacture (YOM)
yom = st.sidebar.selectbox(
    "Select Year of Manufacture (YOM)", 
    options=["All"] + sorted(data['year_of_manufacture'].unique()),
    key="yom_filter"  # Unique key
)

# Filter for Year-Month (YY/MM) Range using two dropdowns
start_year_month = st.sidebar.selectbox(
    "Select Start Year-Month (YY/MM)",
    options=sorted(data['year_month'].unique()),
    key="start_year_month_filter"
)

end_year_month = st.sidebar.selectbox(
    "Select End Year-Month (YY/MM)",
    options=sorted(data['year_month'].unique()),
    index=len(sorted(data['year_month'].unique())) - 1,  # Default to the last value
    key="end_year_month_filter"
)

# Filter data based on user selection
filtered_data = data.copy()
if brand != "All":
    filtered_data = filtered_data[filtered_data['brand'] == brand]
if model != "All":
    filtered_data = filtered_data[filtered_data['model'] == model]
if yom != "All":
    filtered_data = filtered_data[filtered_data['year_of_manufacture'] == int(yom)]
if start_year_month and end_year_month:
    filtered_data = filtered_data[
        (filtered_data['year_month'] >= start_year_month) & (filtered_data['year_month'] <= end_year_month)
    ]

# Main Dashboard
st.title("Market Value Dashboard")
st.write("Use the filters in the sidebar to narrow down the results.")

# Navigation Button to Hello Page
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Go to Hello Page"):
        st.experimental_set_query_params(page="hello")
with col2:
    if st.button("Go to Blue T Page"):
        st.experimental_set_query_params(page="Blue T")
with col3:
    if st.button("Go to Data Management Page"):
        st.experimental_set_query_params(page="data_management")
# Statistics Section
st.subheader("Summary Statistics")

if not filtered_data.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Number of data points
    col1.metric("Number of Data", len(filtered_data))
    
    # Highest price
    col2.metric("Highest Price", f"{filtered_data['price'].max():,.2f}")
    
    # Lowest price
    col3.metric("Lowest Price", f"{filtered_data['price'].min():,.2f}")
    
    # Median price
    col4.metric("Median Price", f"{filtered_data['price'].median():,.2f}")
    
    # Average price
    col5.metric("Average Price", f"{filtered_data['price'].mean():,.2f}")
else:
    st.warning("No data matches the selected filters.")

# Data Table
st.subheader("Filtered Data")
st.dataframe(filtered_data)
