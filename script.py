# First, let's create a comprehensive data processing module for the Vahan Dashboard project
# This will simulate the structure and functionality we would need for the actual project

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import random
from typing import Dict, List, Tuple

# Create sample vehicle registration data that mirrors Vahan Dashboard structure
def generate_sample_vahan_data():
    """
    Generate comprehensive sample data that mimics Vahan Dashboard structure
    """
    
    # Vehicle categories and classes from Vahan dashboard
    vehicle_categories = {
        "2W": ["M-CYCLE/SCOOTER", "MOPED", "MOTORISED CYCLE (CC > 25CC)"],
        "3W": ["THREE WHEELER (GOODS)", "THREE WHEELER (PASSENGER)", "THREE WHEELER (PERSONAL)", "E-RICKSHAW(P)"],
        "4W": ["MOTOR CAR", "OMNI BUS", "BUS", "GOODS CARRIER", "LUXURY CAB", "MOTOR CAB"]
    }
    
    # Major manufacturers from research
    manufacturers = {
        "2W": ["HERO MOTOCORP LTD", "HONDA MOTORCYCLE & SCOOTER INDIA", "TVS MOTOR COMPANY LTD", 
               "BAJAJ AUTO LIMITED", "ROYAL ENFIELD", "YAMAHA MOTOR INDIA", "SUZUKI MOTORCYCLE"],
        "3W": ["BAJAJ AUTO LIMITED", "TVS MOTOR COMPANY LTD", "MAHINDRA & MAHINDRA", 
               "PIAGGIO VEHICLES PVT LTD", "ATUL AUTO LIMITED"],
        "4W": ["MARUTI SUZUKI INDIA LTD", "HYUNDAI MOTOR INDIA LTD", "TATA MOTORS LTD", 
               "MAHINDRA & MAHINDRA", "TOYOTA KIRLOSKAR MOTOR", "KIA MOTORS INDIA", 
               "HONDA CARS INDIA LTD", "MG MOTOR INDIA"]
    }
    
    # Indian states from Vahan data
    states = [
        "Andhra Pradesh", "Bihar", "Chhattisgarh", "Delhi", "Goa", "Gujarat", 
        "Haryana", "Karnataka", "Kerala", "Maharashtra", "Madhya Pradesh", 
        "Odisha", "Punjab", "Rajasthan", "Tamil Nadu", "Uttar Pradesh", "West Bengal"
    ]
    
    # Generate monthly data from 2020 to 2024
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    data_records = []
    
    # Generate data for each month
    current_date = start_date
    while current_date <= end_date:
        year = current_date.year
        month = current_date.month
        month_name = current_date.strftime("%B")
        
        # Generate data for each state
        for state in states:
            # Generate data for each vehicle category
            for category, classes in vehicle_categories.items():
                for vehicle_class in classes:
                    # Generate data for each manufacturer relevant to this category
                    for manufacturer in manufacturers[category]:
                        
                        # Base registration count with realistic trends
                        base_count = {
                            "2W": random.randint(5000, 25000),
                            "3W": random.randint(500, 3000),
                            "4W": random.randint(1000, 8000)
                        }[category]
                        
                        # Apply market share adjustments for major players
                        if manufacturer in ["HERO MOTOCORP LTD", "MARUTI SUZUKI INDIA LTD"]:
                            base_count *= random.uniform(1.5, 2.5)
                        elif manufacturer in ["HONDA MOTORCYCLE & SCOOTER INDIA", "HYUNDAI MOTOR INDIA LTD", "TATA MOTORS LTD"]:
                            base_count *= random.uniform(1.2, 1.8)
                        
                        # Apply seasonal variations
                        seasonal_factor = 1.0
                        if month in [3, 4, 10, 11]:  # Peak seasons
                            seasonal_factor = random.uniform(1.2, 1.4)
                        elif month in [6, 7, 8]:  # Monsoon dip
                            seasonal_factor = random.uniform(0.7, 0.9)
                        
                        # Apply COVID impact for 2020-2021
                        if year == 2020 and month >= 4:
                            seasonal_factor *= random.uniform(0.3, 0.6)
                        elif year == 2021:
                            seasonal_factor *= random.uniform(0.6, 0.9)
                        
                        # Apply growth trends
                        growth_factor = 1.0
                        if category == "2W":
                            if "ELECTRIC" in manufacturer or "E-" in vehicle_class:
                                growth_factor = 1.0 + (year - 2020) * 0.3  # EV growth
                        
                        final_count = int(base_count * seasonal_factor * growth_factor)
                        final_count = max(1, final_count)  # Ensure at least 1
                        
                        data_records.append({
                            "year": year,
                            "month": month,
                            "month_name": month_name,
                            "state": state,
                            "vehicle_category": category,
                            "vehicle_class": vehicle_class,
                            "manufacturer": manufacturer,
                            "registration_count": final_count,
                            "date": current_date
                        })
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Create DataFrame
    df = pd.DataFrame(data_records)
    
    # Add some derived columns for analysis
    df['quarter'] = df['month'].apply(lambda x: f"Q{(x-1)//3 + 1}")
    df['financial_year'] = df.apply(lambda x: f"FY{x['year']+1}" if x['month'] >= 4 else f"FY{x['year']}", axis=1)
    
    return df

# Generate the sample data
print("Generating comprehensive Vahan dashboard sample data...")
sample_data = generate_sample_vahan_data()

print(f"Generated {len(sample_data)} records")
print(f"Date range: {sample_data['date'].min()} to {sample_data['date'].max()}")
print(f"States covered: {sample_data['state'].nunique()}")
print(f"Vehicle categories: {list(sample_data['vehicle_category'].unique())}")
print(f"Manufacturers: {sample_data['manufacturer'].nunique()}")

# Preview the data
print("\nSample data preview:")
print(sample_data.head(10))

# Save sample data
sample_data.to_csv('vahan_sample_data.csv', index=False)
print("\nSample data saved as 'vahan_sample_data.csv'")