# Weather Data Processing Pipeline

This project implements a data processing pipeline for weather data. The pipeline ingests raw weather data from a CSV file, cleans and transforms it, and outputs the processed data along with visualizations and reports.

## Project Structure

```
weather-data-processing/
├── weather_data_pipeline.py  # Main Python script
├── weather_data.csv          # Input data file
├── outputs/                  # Output directory (created by script)
│   ├── transformed_weather_data.csv     # Cleaned and transformed data
|   ├── transformed_weather_data.xlsx    # Cleaned and transformed data in excel workbook format for better visual  
│   ├── top_cities_temperature_report.md  # Report on top 5 cities by temperature
│   └── city_temperature_chart.png     # Visualization of average temperatures
└── README.md                 # This file
```

## Features

1. **Data Ingestion**: Reads weather data from a CSV file.
2. **Data Cleaning**:
   - Standardizes date formats to YYYY-MM-DD
   - Handles missing values using city-specific and global averages
   - Standardizes weather condition text
3. **Data Transformation**:
   - Adds temperature in Fahrenheit
   - Filters out unknown weather conditions
   - Rounds numeric values for cleaner output
4. **Data Analysis**:
   - Identifies top 5 cities by average temperature
   - Generates a visual bar chart of average temperatures

## Requirements

- Python
- pandas
- numpy
- matplotlib
- seaborn

## Installation

1. Clone this repository or download the source files.
2. Install the required packages:
```bash
pip install pandas numpy matplotlib seaborn
```

## Usage

1. Ensure that `weather_data.csv` is in the same directory as the script.
2. Run the script:
```bash
python weather_data_pipeline.py
```
3. Check the `outputs` directory for results.

## Approach & Challenges

### Data Cleaning Approach

The cleaning process addressed several data quality issues:

1. **Date Standardization**: The original data contained multiple date formats (MM/DD/YYYY, DD-MM-YYYY, DD.MM.YYYY). I implemented a regex-based approach to detect and standardize these formats to YYYY-MM-DD.

2. **Missing Values**: For missing temperature, humidity, and wind speed values, I used a hierarchical approach:
   - First, attempt to fill missing values with the average for that city
   - If city average is not available, use the global average across all cities

3. **Weather Condition Standardization**: I standardized the case of weather conditions (e.g., "RAINY" → "Rainy") and filtered out unknown or missing values.

### Challenges Faced

1. **Inconsistent Date Formats**: The variety of date formats required careful regex pattern matching to ensure correct transformation.

2. **Data Quality Issues**: The dataset contained various forms of missing data (empty cells, "NULL" strings, etc.) that needed consistent handling.

3. **City-Specific Averages**: Some cities had very few data points, making their averages potentially unreliable, but still better than global averages.

## Sample Output

### Transformed Data

The transformed CSV contains cleaned data with standardized dates, cleaned weather conditions, and the addition of temperature in Fahrenheit.

### Top Cities Report

The Markdown report lists the top 5 cities by average temperature in descending order.

### Visualization

The bar chart provides a visual representation of average temperatures across cities, making it easy to compare temperature patterns.

### Project Owner

Hello there, my name is Estifanos Alamirew and I just wanted to say thanks for reviewing my data analysis work. 
