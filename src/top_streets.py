import pandas as pd
import json

# Read the CSV file
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

# Get top 10 streets by total crashes
top_streets = df['Street Full Name (ifnull)'].value_counts().head(15)

# Convert to list of dictionaries
top_streets_data = []
for rank, (street, count) in enumerate(top_streets.items(), 1):
    # Only include if we have a valid street name
    if street and str(street).strip() and street != '0':
        top_streets_data.append({
            'rank': rank,
            'street': street,
            'crashes': int(count),
            'percentage': round((count / len(df)) * 100, 2)
        })

# Keep only top 10
top_streets_data = top_streets_data[:10]

# Save to JSON files
with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/processed/top_streets.json', 'w') as f:
    json.dump(top_streets_data, f, indent=2)

with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/output/top_streets.json', 'w') as f:
    json.dump(top_streets_data, f, indent=2)

print("Top 10 Streets by Crash Count:")
print("=" * 80)
for item in top_streets_data:
    print(f"{item['rank']:2d}. {item['street']:45s} - {item['crashes']:6d} crashes ({item['percentage']:5.2f}%)")
print("\nData saved to: data/processed/top_streets.json and output/top_streets.json")
