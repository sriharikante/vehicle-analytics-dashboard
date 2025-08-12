# Now create the data processing module
data_processing_code = '''
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VahanDataProcessor:
    """
    Comprehensive data processor for Vahan Dashboard data
    Handles data extraction, cleaning, and analysis
    """
    
    def __init__(self, data_source='sample'):
        """
        Initialize the data processor
        
        Args:
            data_source (str): 'sample' for sample data, 'vahan' for web scraping
        """
        self.data_source = data_source
        self.raw_data = None
        self.processed_data = None
        
    def load_sample_data(self, filepath: str = 'vahan_sample_data.csv') -> pd.DataFrame:
        """
        Load sample data for development and testing
        
        Args:
            filepath (str): Path to sample data CSV
            
        Returns:
            pd.DataFrame: Loaded sample data
        """
        try:
            df = pd.read_csv(filepath)
            df['date'] = pd.to_datetime(df['date'])
            logger.info(f"Loaded {len(df)} records from {filepath}")
            self.raw_data = df
            return df
        except Exception as e:
            logger.error(f"Error loading sample data: {e}")
            raise
    
    def scrape_vahan_data(self, states: List[str] = None, 
                         start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        Scrape data from Vahan Dashboard (placeholder implementation)
        
        Args:
            states (List[str]): List of states to scrape
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: Scraped data
        """
        # NOTE: This is a placeholder implementation
        # In production, you would implement actual web scraping logic
        # using Selenium to navigate the Vahan dashboard
        
        logger.warning("Web scraping not implemented in this demo version")
        logger.info("Using sample data instead")
        
        # For demo purposes, return sample data
        return self.load_sample_data()
    
    def clean_and_process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process raw Vahan data
        
        Args:
            df (pd.DataFrame): Raw data
            
        Returns:
            pd.DataFrame: Cleaned and processed data
        """
        logger.info("Starting data cleaning and processing...")
        
        # Create a copy to avoid modifying original
        processed_df = df.copy()
        
        # Data cleaning steps
        processed_df = processed_df.dropna(subset=['registration_count'])
        processed_df = processed_df[processed_df['registration_count'] > 0]
        
        # Standardize manufacturer names
        processed_df['manufacturer_clean'] = processed_df['manufacturer'].str.upper().str.strip()
        
        # Add time-based features
        processed_df['year_month'] = processed_df['date'].dt.to_period('M')
        processed_df['day_of_year'] = processed_df['date'].dt.dayofyear
        
        # Calculate moving averages and trends
        processed_df = self._calculate_growth_metrics(processed_df)
        
        logger.info(f"Data processing complete. {len(processed_df)} records processed.")
        self.processed_data = processed_df
        return processed_df
    
    def _calculate_growth_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate YoY and QoQ growth metrics
        
        Args:
            df (pd.DataFrame): Input data
            
        Returns:
            pd.DataFrame: Data with growth metrics
        """
        result_records = []
        
        # Group by relevant dimensions for growth calculation
        grouping_cols = ['state', 'vehicle_category', 'manufacturer']
        
        for group_key, group_df in df.groupby(grouping_cols):
            group_df = group_df.sort_values('date').copy()
            
            # Calculate YoY growth
            group_df['yoy_growth'] = group_df['registration_count'].pct_change(periods=12) * 100
            
            # Calculate QoQ growth (3-month periods)
            group_df['qoq_growth'] = group_df['registration_count'].pct_change(periods=3) * 100
            
            # Calculate rolling averages
            group_df['ma_3m'] = group_df['registration_count'].rolling(window=3).mean()
            group_df['ma_6m'] = group_df['registration_count'].rolling(window=6).mean()
            group_df['ma_12m'] = group_df['registration_count'].rolling(window=12).mean()
            
            result_records.append(group_df)
        
        return pd.concat(result_records, ignore_index=True)
    
    def get_category_summary(self, df: pd.DataFrame = None) -> Dict:
        """
        Get summary statistics by vehicle category
        
        Args:
            df (pd.DataFrame): Data to analyze (uses processed_data if None)
            
        Returns:
            Dict: Summary statistics
        """
        if df is None:
            df = self.processed_data
        
        if df is None:
            raise ValueError("No data available. Please load/process data first.")
        
        summary = {}
        
        for category in df['vehicle_category'].unique():
            cat_data = df[df['vehicle_category'] == category]
            
            summary[category] = {
                'total_registrations': cat_data['registration_count'].sum(),
                'avg_monthly_registrations': cat_data['registration_count'].mean(),
                'top_manufacturers': cat_data.groupby('manufacturer')['registration_count'].sum().nlargest(5).to_dict(),
                'top_states': cat_data.groupby('state')['registration_count'].sum().nlargest(5).to_dict(),
                'latest_yoy_growth': cat_data['yoy_growth'].dropna().iloc[-1] if not cat_data['yoy_growth'].dropna().empty else 0
            }
        
        return summary
    
    def get_manufacturer_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Get comprehensive manufacturer analysis
        
        Args:
            df (pd.DataFrame): Data to analyze
            
        Returns:
            pd.DataFrame: Manufacturer analysis
        """
        if df is None:
            df = self.processed_data
        
        # Group by manufacturer and calculate metrics
        manufacturer_stats = df.groupby('manufacturer').agg({
            'registration_count': ['sum', 'mean', 'count'],
            'yoy_growth': 'mean',
            'qoq_growth': 'mean'
        }).round(2)
        
        # Flatten column names
        manufacturer_stats.columns = ['total_registrations', 'avg_monthly', 'data_points', 
                                    'avg_yoy_growth', 'avg_qoq_growth']
        
        # Calculate market share
        total_market = manufacturer_stats['total_registrations'].sum()
        manufacturer_stats['market_share_pct'] = (
            manufacturer_stats['total_registrations'] / total_market * 100
        ).round(2)
        
        # Sort by total registrations
        manufacturer_stats = manufacturer_stats.sort_values('total_registrations', ascending=False)
        
        return manufacturer_stats
    
    def get_time_series_data(self, groupby_cols: List[str] = None, 
                           date_range: Tuple[str, str] = None) -> pd.DataFrame:
        """
        Get time series data for visualization
        
        Args:
            groupby_cols (List[str]): Columns to group by
            date_range (Tuple[str, str]): Date range filter
            
        Returns:
            pd.DataFrame: Time series data
        """
        if self.processed_data is None:
            raise ValueError("No processed data available")
        
        df = self.processed_data.copy()
        
        # Apply date filter if provided
        if date_range:
            start_date, end_date = date_range
            df = df[
                (df['date'] >= pd.to_datetime(start_date)) & 
                (df['date'] <= pd.to_datetime(end_date))
            ]
        
        # Default grouping
        if groupby_cols is None:
            groupby_cols = ['year_month', 'vehicle_category']
        
        # Aggregate data
        time_series = df.groupby(groupby_cols).agg({
            'registration_count': 'sum',
            'yoy_growth': 'mean',
            'qoq_growth': 'mean'
        }).reset_index()
        
        return time_series
    
    def export_processed_data(self, filepath: str = 'processed_vahan_data.csv') -> str:
        """
        Export processed data to CSV
        
        Args:
            filepath (str): Output file path
            
        Returns:
            str: Path to exported file
        """
        if self.processed_data is None:
            raise ValueError("No processed data to export")
        
        self.processed_data.to_csv(filepath, index=False)
        logger.info(f"Processed data exported to {filepath}")
        return filepath

# Helper functions for data filtering and selection
def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """Filter DataFrame by date range"""
    return df[
        (df['date'] >= pd.to_datetime(start_date)) & 
        (df['date'] <= pd.to_datetime(end_date))
    ]

def filter_by_categories(df: pd.DataFrame, categories: List[str]) -> pd.DataFrame:
    """Filter DataFrame by vehicle categories"""
    return df[df['vehicle_category'].isin(categories)]

def filter_by_manufacturers(df: pd.DataFrame, manufacturers: List[str]) -> pd.DataFrame:
    """Filter DataFrame by manufacturers"""
    return df[df['manufacturer'].isin(manufacturers)]

def get_top_performers(df: pd.DataFrame, metric: str = 'registration_count', 
                      groupby: str = 'manufacturer', n: int = 10) -> pd.DataFrame:
    """Get top performers by specified metric"""
    return df.groupby(groupby)[metric].sum().nlargest(n).reset_index()
'''

# Save the data processing module
with open('data_processing.py', 'w') as f:
    f.write(data_processing_code)

print("Created data_processing.py - Comprehensive data processing module")
print("Features included:")
print("- VahanDataProcessor class with sample data loading")
print("- Data cleaning and processing functions")
print("- Growth metrics calculation (YoY, QoQ)")
print("- Category and manufacturer analysis")
print("- Time series data preparation")
print("- Export functionality")
print("- Web scraping placeholder for production use")