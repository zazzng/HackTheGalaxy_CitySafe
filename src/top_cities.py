import pandas as pd
import json

# Read the CSV file
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

# Get top 10 cities by total crashes
top_cities = df['Municipality Name (ifnull)'].value_counts().head(10)

# Convert to list of dictionaries
top_cities_data = []
for rank, (city, count) in enumerate(top_cities.items(), 1):
    top_cities_data.append({
        'rank': rank,
        'city': city,
        'crashes': int(count),
        'percentage': round((count / len(df)) * 100, 1)
    })

# Save to JSON file
with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/processed/top_cities.json', 'w') as f:
    json.dump(top_cities_data, f, indent=2)

with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/output/top_cities.json', 'w') as f:
    json.dump(top_cities_data, f, indent=2)

print("Top 10 Cities by Crash Count:")
print("=" * 70)
for item in top_cities_data:
    print(f"{item['rank']:2d}. {item['city']:30s} - {item['crashes']:7d} crashes ({item['percentage']:5.1f}%)")
print("\nData saved to: data/processed/top_cities.json and output/top_cities.json")
