#!/usr/bin/env python3
"""
Weather Data Processing Pipeline

This script processes weather data from a CSV file, cleans and transforms it,
and saves the results to output files.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re

def create_output_dir():
    """Create output directory if it doesn't exist."""
    if not os.path.exists('outputs'):
        os.makedirs('outputs')
        print("Created 'outputs' directory")

def ingest_data(filepath):
    """Ingest data from CSV file."""
    print(f"Ingesting data from {filepath}...")
    return pd.read_csv(filepath)

def clean_dates(df):
    """Standardize dates to YYYY-MM-DD format."""
    print("Cleaning and standardizing dates...")
    
    # First, drop rows where date is completely missing
    df = df.dropna(subset=['date'])
    
    # Function to convert various date formats to YYYY-MM-DD
    def standardize_date(date_str):
        if not isinstance(date_str, str) or pd.isna(date_str):
            return None
        
        # Handle different date formats
        patterns = [
            # DD/MM/YYYY or MM/DD/YYYY (assuming mostly MM/DD/YYYY based on data)
            (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
            # DD-MM-YYYY or MM-DD-YYYY
            (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
            # DD.MM.YYYY or MM.DD.YYYY
            (r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', lambda m: f"{m.group(3)}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
        ]
        
        for pattern, formatter in patterns:
            match = re.match(pattern, date_str)
            if match:
                return formatter(match)
        
        return None
    
    # Apply the standardization function
    df['standardized_date'] = df['date'].apply(standardize_date)
    
    # Drop rows where standardization failed
    df = df.dropna(subset=['standardized_date'])
    
    # Convert to datetime for validation and convert back to string
    df['standardized_date'] = pd.to_datetime(df['standardized_date'], errors='coerce')
    # Drop any rows that failed datetime conversion
    df = df.dropna(subset=['standardized_date'])
    # Convert back to string format YYYY-MM-DD
    df['standardized_date'] = df['standardized_date'].dt.strftime('%Y-%m-%d')
    
    # Replace original date with standardized one
    df['date'] = df['standardized_date']
    df = df.drop('standardized_date', axis=1)
    
    return df

def clean_weather_conditions(df):
    """Standardize weather conditions and filter out Unknown entries."""
    print("Cleaning weather conditions...")
    
    # Standardize weather condition values (lowercase everything then capitalize first letter)
    df['weather_condition'] = df['weather_condition'].str.lower().str.capitalize()
    
    # Replace 'NULL' or None values with NaN
    df['weather_condition'] = df['weather_condition'].replace({'Null': np.nan, 'NULL': np.nan})
    
    # Filter out rows where weather_condition is Unknown or NaN
    df = df[~((df['weather_condition'] == 'Unknown') | 
              df['weather_condition'].isna())]
    
    return df

def handle_missing_values(df):
    """Handle missing values in the dataframe."""
    print("Handling missing values...")
    
    # Calculate average temperature per city
    city_avg_temp = df.groupby('city')['temperature_celsius'].mean()
    
    # Fill missing temperature values with city average
    for city in df['city'].unique():
        if city_avg_temp.get(city) and not pd.isna(city_avg_temp.get(city)):
            city_mask = (df['city'] == city) & df['temperature_celsius'].isna()
            df.loc[city_mask, 'temperature_celsius'] = city_avg_temp.get(city)
    
    # For any remaining NaN temperatures (if a city has all NaN), use the global average
    global_avg_temp = df['temperature_celsius'].mean()
    df['temperature_celsius'] = df['temperature_celsius'].fillna(global_avg_temp)
    
    # For humidity and wind speed, fill with city averages if available, otherwise global average
    for column in ['humidity_percent', 'wind_speed_kph']:
        city_avg = df.groupby('city')[column].mean()
        
        for city in df['city'].unique():
            if city_avg.get(city) and not pd.isna(city_avg.get(city)):
                city_mask = (df['city'] == city) & df[column].isna()
                df.loc[city_mask, column] = city_avg.get(city)
        
        # Fill any remaining NaNs with global average
        global_avg = df[column].mean()
        df[column] = df[column].fillna(global_avg)
    
    return df

def add_fahrenheit_column(df):
    """Add temperature_fahrenheit column using the formula F = C × 9/5 + 32."""
    print("Adding temperature_fahrenheit column...")
    df['temperature_fahrenheit'] = df['temperature_celsius'] * 9/5 + 32
    return df

def round_numeric_columns(df):
    """Round numeric columns to 2 decimal places for cleaner output."""
    for column in ['temperature_celsius', 'temperature_fahrenheit', 'humidity_percent', 'wind_speed_kph']:
        df[column] = df[column].round(2)
    return df

def generate_city_temperature_report(df):
    """Generate a report of the top 5 cities with highest average temperature."""
    print("Generating city temperature report...")
    
    city_avg_temp = df.groupby('city')['temperature_celsius'].mean().round(2).sort_values(ascending=False)
    top_cities = city_avg_temp.head(5)
    
    report_content = "# Top 5 Cities by Average Temperature (Celsius)\n\n"
    for i, (city, temp) in enumerate(top_cities.items(), 1):
        report_content += f"{i}. {city}: {temp}°C\n"
    
    # Save report
    report_path = os.path.join('outputs', 'top_cities_temperature_report.md')
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    print(f"Report saved to {report_path}")
    return top_cities

def generate_temperature_chart(top_cities):
    """Generate a bar chart of average temperature per city."""
    print("Generating temperature chart...")
    
    plt.figure(figsize=(10, 6))
    
    # Use Seaborn for a nicer visual
    chart = sns.barplot(x=top_cities.index, y=top_cities.values)
    
    plt.title('Top 5 Cities by Average Temperature (Celsius)', fontsize=15)
    plt.xlabel('City', fontsize=12)
    plt.ylabel('Average Temperature (°C)', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add temperature values on top of each bar
    for i, temp in enumerate(top_cities.values):
        chart.text(i, temp + 0.1, f"{temp}°C", ha='center')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = os.path.join('outputs', 'city_temperature_chart.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    
    print(f"Chart saved to {chart_path}")

def main():
    """Main function to run the pipeline."""
    print("Starting weather data processing pipeline...")
    
    # Create outputs directory
    create_output_dir()
    
    # Ingest data
    df = ingest_data('weather_data.csv')
    print(f"Ingested {len(df)} rows of data")
    
    # Clean and transform data
    df = clean_dates(df)
    df = clean_weather_conditions(df)
    df = handle_missing_values(df)
    df = add_fahrenheit_column(df)
    df = round_numeric_columns(df)
    
    # Save transformed data
    output_path = os.path.join('outputs', 'transformed_weather_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Transformed data saved to {output_path}")
    
    # Generate report and chart
    top_cities = generate_city_temperature_report(df)
    generate_temperature_chart(top_cities)
    
    print("Pipeline completed successfully!")

if __name__ == "__main__":
    main()
