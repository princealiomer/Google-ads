"""
Google Ads Transparency Data Viewer
A Streamlit app to view and analyze scraped Google Ads data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# Page configuration
st.set_page_config(
    page_title="Google Ads Transparency Viewer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stDownloadButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load sample data from results folder"""
    results_path = Path("results")
    if results_path.exists():
        csv_files = list(results_path.glob("*.csv"))
        if csv_files:
            return pd.read_csv(csv_files[0])
    return None

def parse_ad_count(ad_count_str):
    """Extract numeric value from ad count string (e.g., '~63 ads' -> 63)"""
    if pd.isna(ad_count_str):
        return 0
    try:
        return int(str(ad_count_str).replace('~', '').replace('ads', '').strip())
    except:
        return 0

def parse_location(location_str):
    """Extract country from location string (e.g., 'Based in: South Korea' -> 'South Korea')"""
    if pd.isna(location_str):
        return "Unknown"
    return str(location_str).replace('Based in:', '').strip()

def create_dashboard(df):
    """Create interactive dashboard with visualizations"""
    
    # Parse data for better analysis
    df['ad_count_numeric'] = df['ad-count'].apply(parse_ad_count)
    df['country'] = df['location'].apply(parse_location)
    df['is_verified'] = df['verified-identity-text'].notna() & (df['verified-identity-text'] != '')
    
    # Header
    st.markdown('<div class="main-header">📊 Google Ads Transparency Dashboard</div>', unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Advertisers", len(df))
    
    with col2:
        verified_count = df['is_verified'].sum()
        st.metric("Verified Advertisers", verified_count)
    
    with col3:
        total_ads = df['ad_count_numeric'].sum()
        st.metric("Total Ads", f"~{total_ads:,}")
    
    with col4:
        unique_countries = df['country'].nunique()
        st.metric("Countries", unique_countries)
    
    st.divider()
    
    # Visualizations
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🌍 Geographic", "✅ Verification", "📊 Data Table"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top 10 countries by advertiser count
            country_counts = df['country'].value_counts().head(10)
            fig = px.bar(
                x=country_counts.values,
                y=country_counts.index,
                orientation='h',
                title="Top 10 Countries by Advertiser Count",
                labels={'x': 'Number of Advertisers', 'y': 'Country'},
                color=country_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Ad count distribution
            ad_ranges = pd.cut(df['ad_count_numeric'], bins=[0, 5, 20, 50, 100, float('inf')], 
                              labels=['1-5', '6-20', '21-50', '51-100', '100+'])
            ad_range_counts = ad_ranges.value_counts().sort_index()
            
            fig = px.pie(
                values=ad_range_counts.values,
                names=ad_range_counts.index,
                title="Advertisers by Ad Count Range",
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Geographic distribution
        country_data = df.groupby('country').agg({
            'name': 'count',
            'ad_count_numeric': 'sum',
            'is_verified': 'sum'
        }).reset_index()
        country_data.columns = ['Country', 'Advertisers', 'Total Ads', 'Verified']
        country_data = country_data.sort_values('Advertisers', ascending=False).head(20)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Advertisers',
            x=country_data['Country'],
            y=country_data['Advertisers'],
            marker_color='lightblue'
        ))
        fig.add_trace(go.Bar(
            name='Verified',
            x=country_data['Country'],
            y=country_data['Verified'],
            marker_color='darkblue'
        ))
        
        fig.update_layout(
            title="Top 20 Countries: Advertisers vs Verified",
            xaxis_title="Country",
            yaxis_title="Count",
            barmode='group',
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Country statistics table
        st.subheader("Country Statistics")
        st.dataframe(
            country_data.style.background_gradient(subset=['Advertisers', 'Total Ads'], cmap='Blues'),
            use_container_width=True,
            height=400
        )
    
    with tab3:
        # Verification analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Verification status pie chart
            verification_counts = df['is_verified'].value_counts()
            fig = px.pie(
                values=verification_counts.values,
                names=['Verified' if x else 'Not Verified' for x in verification_counts.index],
                title="Verification Status Distribution",
                color_discrete_map={'Verified': '#2ecc71', 'Not Verified': '#e74c3c'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Verification by top countries
            top_countries = df['country'].value_counts().head(10).index
            verification_by_country = df[df['country'].isin(top_countries)].groupby('country')['is_verified'].agg(['sum', 'count'])
            verification_by_country['percentage'] = (verification_by_country['sum'] / verification_by_country['count'] * 100).round(1)
            verification_by_country = verification_by_country.sort_values('percentage', ascending=False)
            
            fig = px.bar(
                x=verification_by_country.index,
                y=verification_by_country['percentage'],
                title="Verification Rate by Top Countries (%)",
                labels={'x': 'Country', 'y': 'Verification Rate (%)'},
                color=verification_by_country['percentage'],
                color_continuous_scale='Greens'
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # Filters
        st.subheader("🔍 Filter Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_countries = st.multiselect(
                "Select Countries",
                options=sorted(df['country'].unique()),
                default=None
            )
        
        with col2:
            verification_filter = st.selectbox(
                "Verification Status",
                options=["All", "Verified Only", "Not Verified Only"]
            )
        
        with col3:
            min_ads = st.number_input("Minimum Ad Count", min_value=0, value=0)
        
        # Apply filters
        filtered_df = df.copy()
        
        if selected_countries:
            filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
        
        if verification_filter == "Verified Only":
            filtered_df = filtered_df[filtered_df['is_verified'] == True]
        elif verification_filter == "Not Verified Only":
            filtered_df = filtered_df[filtered_df['is_verified'] == False]
        
        if min_ads > 0:
            filtered_df = filtered_df[filtered_df['ad_count_numeric'] >= min_ads]
        
        # Display filtered data
        st.subheader(f"📋 Data Table ({len(filtered_df)} records)")
        
        # Select columns to display
        display_df = filtered_df[['name', 'ad-count', 'location', 'verified-identity-text']].copy()
        display_df.columns = ['Advertiser Name', 'Ad Count', 'Location', 'Verification Status']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            height=500
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name="filtered_google_ads_data.csv",
            mime="text/csv"
        )

def main():
    # Sidebar
    with st.sidebar:
        st.title("📁 Data Source")
        
        # Option to upload file or use sample data
        data_source = st.radio(
            "Choose data source:",
            ["Upload CSV File", "Use Sample Data"]
        )
        
        df = None
        
        if data_source == "Upload CSV File":
            uploaded_file = st.file_uploader(
                "Upload your Google Ads CSV file",
                type=['csv'],
                help="Upload a CSV file with columns: name, material-icon-i, verified-identity-text, ad-count, location"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Loaded {len(df)} records")
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
        
        else:  # Use Sample Data
            df = load_sample_data()
            if df is not None:
                st.success(f"✅ Loaded {len(df)} sample records")
            else:
                st.warning("No sample data found in results folder")
        
        st.divider()
        
        # Information
        st.subheader("ℹ️ About")
        st.info("""
        This app displays and analyzes data from the Google Ads Transparency Center.
        
        **Features:**
        - Interactive visualizations
        - Country-based analysis
        - Verification status tracking
        - Data filtering and export
        """)
        
        st.divider()
        
        # Instructions for scraping
        with st.expander("🔧 How to Scrape Data"):
            st.markdown("""
            To scrape new data locally:
            
            1. Install dependencies:
               ```bash
               pip install -r requirements-scraper.txt
               playwright install chromium
               ```
            
            2. Run the scraper:
               ```bash
               python scrape_google_ads_transparency.py
               ```
            
            3. Upload the generated CSV file here!
            """)
    
    # Main content
    if df is not None:
        # Validate required columns
        required_columns = ['name', 'ad-count', 'location']
        if all(col in df.columns for col in required_columns):
            create_dashboard(df)
        else:
            st.error(f"❌ CSV file must contain columns: {', '.join(required_columns)}")
            st.write("Found columns:", list(df.columns))
    else:
        # Welcome screen
        st.markdown('<div class="main-header">📊 Google Ads Transparency Viewer</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### Welcome! 👋
        
        This application helps you visualize and analyze Google Ads Transparency data.
        
        **Get Started:**
        1. Upload a CSV file using the sidebar, or
        2. Use the sample data if available
        
        **What you'll see:**
        - 📈 Interactive charts and graphs
        - 🌍 Geographic distribution of advertisers
        - ✅ Verification status analysis
        - 📊 Filterable data tables
        """)
        
        # Show sample data structure
        with st.expander("📋 Expected CSV Format"):
            sample_data = {
                'name': ['Advertiser A', 'Advertiser B'],
                'material-icon-i': ['how_to_reg', ''],
                'verified-identity-text': ['Advertiser has verified their identity', ''],
                'ad-count': ['~63 ads', '~12 ads'],
                'location': ['Based in: South Korea', 'Based in: United States']
            }
            st.dataframe(pd.DataFrame(sample_data))

if __name__ == "__main__":
    main()
