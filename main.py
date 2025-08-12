
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import datetime, timedelta, date
from data_processing import VahanDataProcessor, filter_by_date_range, filter_by_categories, filter_by_manufacturers

# Suppress warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Vahan Dashboard Analytics - Financially Free",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
    }

    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }

    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #b3d9ff;
        margin: 1rem 0;
    }

    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }

    .stSelectbox > div > div > select {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

@st.cache_data
def load_and_process_data():
    """Load and process data with caching for performance"""
    processor = VahanDataProcessor(data_source='sample')
    raw_data = processor.load_sample_data()
    processed_data = processor.clean_and_process_data(raw_data)
    return processor, processed_data

def create_kpi_metrics(data):
    """Create KPI metrics for the dashboard"""
    total_registrations = data['registration_count'].sum()
    unique_manufacturers = data['manufacturer'].nunique()
    unique_states = data['state'].nunique()
    latest_month_data = data[data['date'] == data['date'].max()]
    latest_month_registrations = latest_month_data['registration_count'].sum()

    # Calculate YoY growth for latest available data
    latest_yoy = data['yoy_growth'].dropna().iloc[-100:].mean() if not data['yoy_growth'].dropna().empty else 0

    return {
        'total_registrations': total_registrations,
        'unique_manufacturers': unique_manufacturers,
        'unique_states': unique_states,
        'latest_month_registrations': latest_month_registrations,
        'avg_yoy_growth': latest_yoy
    }

def create_time_series_chart(data, metric='registration_count', groupby='vehicle_category'):
    """Create interactive time series chart"""
    # Aggregate data by month and category
    monthly_data = data.groupby(['year_month', groupby])[metric].sum().reset_index()
    monthly_data['date'] = monthly_data['year_month'].astype(str)

    fig = px.line(
        monthly_data, 
        x='date', 
        y=metric, 
        color=groupby,
        title=f'{metric.replace("_", " ").title()} Trend Over Time',
        labels={
            'date': 'Year-Month',
            metric: metric.replace('_', ' ').title(),
            groupby: groupby.replace('_', ' ').title()
        }
    )

    fig.update_layout(
        hovermode='x unified',
        xaxis_tickangle=-45,
        height=500
    )

    return fig

def create_market_share_chart(data, dimension='manufacturer', top_n=10):
    """Create market share visualization"""
    market_data = data.groupby(dimension)['registration_count'].sum().nlargest(top_n)

    fig = px.pie(
        values=market_data.values,
        names=market_data.index,
        title=f'Market Share by {dimension.replace("_", " ").title()} (Top {top_n})'
    )

    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=500)

    return fig

def create_growth_analysis_chart(data):
    """Create growth analysis visualization"""
    # Filter out infinite values and get recent data
    growth_data = data[data['yoy_growth'].notna() & np.isfinite(data['yoy_growth'])].copy()

    if growth_data.empty:
        return go.Figure().add_annotation(
            text="No growth data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )

    # Get latest growth data by manufacturer
    latest_growth = growth_data.loc[growth_data.groupby('manufacturer')['date'].idxmax()]
    latest_growth = latest_growth.nlargest(15, 'registration_count')

    fig = px.bar(
        latest_growth,
        x='manufacturer',
        y='yoy_growth',
        color='vehicle_category',
        title='Year-over-Year Growth Rate by Manufacturer',
        labels={'yoy_growth': 'YoY Growth (%)', 'manufacturer': 'Manufacturer'}
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )

    return fig

def create_state_wise_analysis(data):
    """Create state-wise analysis visualization"""
    state_data = data.groupby('state').agg({
        'registration_count': 'sum',
        'yoy_growth': 'mean'
    }).reset_index()

    state_data = state_data.sort_values('registration_count', ascending=False).head(15)

    fig = px.bar(
        state_data,
        x='state',
        y='registration_count',
        title='Total Vehicle Registrations by State',
        labels={'registration_count': 'Total Registrations', 'state': 'State'}
    )

    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )

    return fig

def main():
    """Main dashboard application"""

    # Header
    st.markdown('<h1 class="main-header">🚗 Vahan Dashboard Analytics</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Comprehensive Vehicle Registration Data Analysis Platform</p>', unsafe_allow_html=True)

    # Load data
    with st.spinner('Loading and processing data...'):
        if st.session_state.data_processor is None:
            processor, processed_data = load_and_process_data()
            st.session_state.data_processor = processor
            st.session_state.processed_data = processed_data
        else:
            processor = st.session_state.data_processor
            processed_data = st.session_state.processed_data

    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Dashboard Filters")

    # Date range filter
    min_date = processed_data['date'].min().date()
    max_date = processed_data['date'].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Vehicle category filter
    categories = st.sidebar.multiselect(
        "Vehicle Categories",
        options=list(processed_data['vehicle_category'].unique()),
        default=list(processed_data['vehicle_category'].unique())
    )

    # State filter
    top_states = processed_data.groupby('state')['registration_count'].sum().nlargest(10).index.tolist()
    selected_states = st.sidebar.multiselect(
        "States",
        options=list(processed_data['state'].unique()),
        default=top_states
    )

    # Manufacturer filter
    top_manufacturers = processed_data.groupby('manufacturer')['registration_count'].sum().nlargest(10).index.tolist()
    selected_manufacturers = st.sidebar.multiselect(
        "Manufacturers",
        options=list(processed_data['manufacturer'].unique()),
        default=top_manufacturers
    )

    # Apply filters
    filtered_data = processed_data.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filter_by_date_range(
            filtered_data, 
            start_date.strftime('%Y-%m-%d'), 
            end_date.strftime('%Y-%m-%d')
        )

    if categories:
        filtered_data = filter_by_categories(filtered_data, categories)

    if selected_states:
        filtered_data = filtered_data[filtered_data['state'].isin(selected_states)]

    if selected_manufacturers:
        filtered_data = filter_by_manufacturers(filtered_data, selected_manufacturers)

    # Check if filtered data is empty
    if filtered_data.empty:
        st.error("No data available for the selected filters. Please adjust your selection.")
        return

    # KPI Metrics
    st.markdown("## 📊 Key Performance Indicators")
    kpis = create_kpi_metrics(filtered_data)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Registrations",
            f"{kpis['total_registrations']:,.0f}",
            help="Total vehicle registrations in selected period"
        )

    with col2:
        st.metric(
            "Manufacturers",
            f"{kpis['unique_manufacturers']:,}",
            help="Number of unique manufacturers"
        )

    with col3:
        st.metric(
            "States Covered",
            f"{kpis['unique_states']:,}",
            help="Number of states in analysis"
        )

    with col4:
        st.metric(
            "Latest Month",
            f"{kpis['latest_month_registrations']:,.0f}",
            help="Registrations in most recent month"
        )

    with col5:
        st.metric(
            "Avg YoY Growth",
            f"{kpis['avg_yoy_growth']:.1f}%",
            help="Average year-over-year growth rate"
        )

    # Main charts section
    st.markdown("## 📈 Trend Analysis")

    # Time series analysis
    col1, col2 = st.columns(2)

    with col1:
        time_series_fig = create_time_series_chart(filtered_data, 'registration_count', 'vehicle_category')
        st.plotly_chart(time_series_fig, use_container_width=True)

    with col2:
        market_share_fig = create_market_share_chart(filtered_data, 'manufacturer', 8)
        st.plotly_chart(market_share_fig, use_container_width=True)

    # Growth and regional analysis
    st.markdown("## 🚀 Growth & Regional Analysis")

    col1, col2 = st.columns(2)

    with col1:
        growth_fig = create_growth_analysis_chart(filtered_data)
        st.plotly_chart(growth_fig, use_container_width=True)

    with col2:
        state_fig = create_state_wise_analysis(filtered_data)
        st.plotly_chart(state_fig, use_container_width=True)

    # Detailed analysis section
    st.markdown("## 🔍 Detailed Analysis")

    tab1, tab2, tab3 = st.tabs(["Manufacturer Analysis", "Category Breakdown", "Data Export"])

    with tab1:
        st.markdown("### Top Manufacturers Performance")
        manufacturer_analysis = processor.get_manufacturer_analysis(filtered_data)
        st.dataframe(
            manufacturer_analysis.head(15),
            use_container_width=True
        )

    with tab2:
        st.markdown("### Vehicle Category Summary")
        category_summary = processor.get_category_summary(filtered_data)

        for category, stats in category_summary.items():
            with st.expander(f"📋 {category} Analysis"):
                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Total Registrations", f"{stats['total_registrations']:,.0f}")
                    st.metric("Avg Monthly", f"{stats['avg_monthly_registrations']:,.0f}")
                    st.metric("YoY Growth", f"{stats['latest_yoy_growth']:.1f}%")

                with col2:
                    st.write("**Top Manufacturers:**")
                    for mfr, count in list(stats['top_manufacturers'].items())[:5]:
                        st.write(f"• {mfr}: {count:,.0f}")

    with tab3:
        st.markdown("### Export Filtered Data")

        export_format = st.selectbox("Export Format", ["CSV", "Excel"])

        if st.button("Generate Export File"):
            if export_format == "CSV":
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"vahan_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                # For Excel export, we'll use CSV for this demo
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    label="Download Data",
                    data=csv_data,
                    file_name=f"vahan_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    # Investor insights section
    st.markdown("## 💼 Investor Insights")

    insights_col1, insights_col2 = st.columns(2)

    with insights_col1:
        st.markdown("""
        <div class="insight-box">
        <h4>🎯 Key Market Trends</h4>
        <ul>
            <li><strong>Two-Wheeler Dominance:</strong> 2W segment continues to lead registrations</li>
            <li><strong>Electric Growth:</strong> EV adoption showing accelerated growth</li>
            <li><strong>Regional Patterns:</strong> Southern and western states driving growth</li>
            <li><strong>Manufacturer Consolidation:</strong> Top 5 players control majority market</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with insights_col2:
        st.markdown("""
        <div class="insight-box">
        <h4>📊 Investment Opportunities</h4>
        <ul>
            <li><strong>EV Infrastructure:</strong> Growing demand for charging networks</li>
            <li><strong>Tier-2 Cities:</strong> Emerging markets with high growth potential</li>
            <li><strong>After-sales Services:</strong> Service sector expansion opportunities</li>
            <li><strong>Technology Integration:</strong> Connected vehicle solutions</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>Vahan Dashboard Analytics | Built for Financially Free Internship Assignment | 
        Data Source: Government of India - Vahan Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
