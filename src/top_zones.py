import pandas as pd
import json

# Read the CSV file
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

# Get top 10 regions by total crashes
top_regions = df['Region'].value_counts().head(10)

# Convert to list of dictionaries
top_zones_data = []
for rank, (region, count) in enumerate(top_regions.items(), 1):
    top_zones_data.append({
        'rank': rank,
        'zone': region,
        'crashes': int(count),
        'percentage': round((count / len(df)) * 100, 1)
    })

# Save to JSON file
with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/processed/top_zones.json', 'w') as f:
    json.dump(top_zones_data, f, indent=2)

print("Top 10 Zones by Crash Count:")
print("=" * 60)
for item in top_zones_data:
    print(f"{item['rank']:2d}. {item['zone']:30s} - {item['crashes']:7d} crashes ({item['percentage']:5.1f}%)")
print("\nData saved to: data/processed/top_zones.json")
