import csv
import re
from collections import defaultdict

def analyze_april_solar_data():
    """
    Analyze solar energy production data for April months
    Calculate averages for UTC times: 03, 06, 09, 12, 15
    """
    
    print("Reading CSV file...")
    
    # Read the file and find data start
    with open('timeseri.csv', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Find where the actual data starts
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('time,G(i),H_sun,T2m,WS10m,Int'):
            data_start = i + 1
            break
    
    print(f"Data starts at line {data_start}")
    
    # Parse April data
    april_data = []
    total_records = 0
    
    for i in range(data_start, len(lines)):
        line = lines[i].strip()
        if line and ',' in line:
            total_records += 1
            parts = line.split(',')
            if len(parts) >= 6:
                time_str = parts[0]
                # Check if it's April data (format: YYYY04DD:HHMM)
                if re.match(r'^\d{4}04\d{2}:\d{4}$', time_str):
                    try:
                        g_i = float(parts[1])
                        h_sun = float(parts[2])
                        t2m = float(parts[3])
                        ws10m = float(parts[4])
                        intensity = float(parts[5])
                        
                        # Extract hour from time string
                        hour = int(time_str.split(':')[1][:2])
                        
                        april_data.append({
                            'time': time_str,
                            'hour': hour,
                            'G(i)': g_i,
                            'H_sun': h_sun,
                            'T2m': t2m,
                            'WS10m': ws10m,
                            'Int': intensity
                        })
                    except ValueError:
                        continue
    
    print(f"Total records processed: {total_records}")
    print(f"April records found: {len(april_data)}")
    
    if len(april_data) == 0:
        print("No April data found!")
        return
    
    # Filter for target hours
    target_hours = [3, 6, 9, 12, 15]
    filtered_data = [record for record in april_data if record['hour'] in target_hours]
    
    print(f"Records for target hours (03, 06, 09, 12, 15): {len(filtered_data)}")
    
    # Calculate averages for each hour
    print("\n=== APRIL SOLAR ENERGY PRODUCTION AVERAGES ===")
    print("UTC Time | G(i) Avg | H_sun Avg | T2m Avg | WS10m Avg | Int Avg | Count")
    print("-" * 80)
    
    results = {}
    
    for hour in target_hours:
        hour_data = [record for record in filtered_data if record['hour'] == hour]
        
        if len(hour_data) > 0:
            g_i_avg = sum(record['G(i)'] for record in hour_data) / len(hour_data)
            h_sun_avg = sum(record['H_sun'] for record in hour_data) / len(hour_data)
            t2m_avg = sum(record['T2m'] for record in hour_data) / len(hour_data)
            ws10m_avg = sum(record['WS10m'] for record in hour_data) / len(hour_data)
            int_avg = sum(record['Int'] for record in hour_data) / len(hour_data)
            
            results[hour] = {
                'G(i)': g_i_avg,
                'H_sun': h_sun_avg,
                'T2m': t2m_avg,
                'WS10m': ws10m_avg,
                'Int': int_avg,
                'count': len(hour_data)
            }
            
            print(f"   {hour:02d}   | {g_i_avg:8.2f} | {h_sun_avg:8.2f} | {t2m_avg:6.2f} | {ws10m_avg:8.2f} | {int_avg:6.2f} | {len(hour_data):5d}")
        else:
            print(f"   {hour:02d}   | No data found")
    
    # Summary statistics
    unique_days = set(record['time'][:8] for record in april_data)
    unique_years = set(record['time'][:4] for record in april_data)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total April days analyzed: {len(unique_days)}")
    print(f"Years covered: {sorted(unique_years)}")
    
    # Show sample of data for verification
    print(f"\n=== SAMPLE DATA (First 5 April records) ===")
    for i, record in enumerate(april_data[:5]):
        print(f"{record['time']} | G(i): {record['G(i)']:6.2f} | H_sun: {record['H_sun']:6.2f} | T2m: {record['T2m']:6.2f} | WS10m: {record['WS10m']:6.2f} | Int: {record['Int']:6.2f}")
    
    return results

if __name__ == "__main__":
    try:
        results = analyze_april_solar_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
