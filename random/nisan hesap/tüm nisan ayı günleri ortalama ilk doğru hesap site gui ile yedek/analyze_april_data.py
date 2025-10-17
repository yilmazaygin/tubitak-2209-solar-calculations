import pandas as pd
import numpy as np
from datetime import datetime
import re

def analyze_april_solar_data():
    """
    Analyze solar energy production data for April months
    Calculate averages for UTC times: 03, 06, 09, 12, 15
    """
    
    # Read the CSV file
    print("Reading CSV file...")
    
    # Read the file line by line to handle the header information
    with open('timeseri.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Find where the actual data starts (after the header lines)
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('time,G(i),H_sun,T2m,WS10m,Int'):
            data_start = i + 1
            break
    
    # Extract data lines
    data_lines = lines[data_start:]
    
    # Parse the data
    data = []
    for line in data_lines:
        line = line.strip()
        if line and ',' in line:
            parts = line.split(',')
            if len(parts) >= 6:
                time_str = parts[0]
                try:
                    g_i = float(parts[1])
                    h_sun = float(parts[2])
                    t2m = float(parts[3])
                    ws10m = float(parts[4])
                    intensity = float(parts[5])
                    
                    data.append({
                        'time': time_str,
                        'G(i)': g_i,
                        'H_sun': h_sun,
                        'T2m': t2m,
                        'WS10m': ws10m,
                        'Int': intensity
                    })
                except ValueError:
                    continue
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    print(f"Total records loaded: {len(df)}")
    
    # Extract April data
    april_data = df[df['time'].str.contains(r'^\d{4}04\d{2}:\d{4}$')]
    print(f"April records found: {len(april_data)}")
    
    if len(april_data) == 0:
        print("No April data found!")
        return
    
    # Extract hour from time string
    april_data['hour'] = april_data['time'].str.extract(r':(\d{2})\d{2}$')[0].astype(int)
    
    # Filter for the specified UTC times
    target_hours = [3, 6, 9, 12, 15]
    filtered_data = april_data[april_data['hour'].isin(target_hours)]
    
    print(f"Records for target hours (03, 06, 09, 12, 15): {len(filtered_data)}")
    
    # Calculate averages for each hour
    print("\n=== APRIL SOLAR ENERGY PRODUCTION AVERAGES ===")
    print("UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg")
    print("-" * 70)
    
    results = {}
    
    for hour in target_hours:
        hour_data = filtered_data[filtered_data['hour'] == hour]
        
        if len(hour_data) > 0:
            g_i_avg = hour_data['G(i)'].mean()
            h_sun_avg = hour_data['H_sun'].mean()
            t2m_avg = hour_data['T2m'].mean()
            ws10m_avg = hour_data['WS10m'].mean()
            int_avg = hour_data['Int'].mean()
            
            results[hour] = {
                'G(i)': g_i_avg,
                'H_sun': h_sun_avg,
                'T2m': t2m_avg,
                'WS10m': ws10m_avg,
                'Int': int_avg,
                'count': len(hour_data)
            }
            
            print(f"   {hour:02d}   | {g_i_avg:8.2f} | {h_sun_avg:8.2f} | {t2m_avg:6.2f} | {ws10m_avg:8.2f} | {int_avg:6.2f}")
        else:
            print(f"   {hour:02d}   | No data found")
    
    # Summary statistics
    print(f"\n=== SUMMARY ===")
    print(f"Total April days analyzed: {len(april_data['time'].str[:8].unique())}")
    print(f"Years covered: {sorted(april_data['time'].str[:4].unique())}")
    
    # Show sample of data for verification
    print(f"\n=== SAMPLE DATA (First 5 April records) ===")
    print(april_data[['time', 'G(i)', 'H_sun', 'T2m', 'WS10m', 'Int']].head())
    
    return results

if __name__ == "__main__":
    results = analyze_april_solar_data()
