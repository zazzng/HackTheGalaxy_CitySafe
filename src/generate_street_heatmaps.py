import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import os

# Read the CSV file and top streets data
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/output/top_streets.json') as f:
    top_streets_list = json.load(f)

output_dir = '/Users/jana/Documents/HackTheGalaxy_CitySafe/output'

print("Generating street-specific heatmaps...\n")

for street_info in top_streets_list:
    street_name = street_info['street']
    print(f"Processing {street_name}...")
    
    # Filter data for this street
    street_data = df[df['Street Full Name (ifnull)'] == street_name].copy()
    
    # Get valid coordinates
    street_data = street_data.dropna(subset=['Latitude', 'Longitude'])
    street_data = street_data[(street_data['Latitude'] != 0) & (street_data['Longitude'] != 0)]
    
    if len(street_data) == 0:
        print(f"  ⚠️  No coordinates found for {street_name}")
        continue
    
    print(f"  ✓ Found {len(street_data):,} crash points")
    
    # Calculate center and bounds
    center_lat = street_data['Latitude'].mean()
    center_lon = street_data['Longitude'].mean()
    
    # Calculate boundaries
    lat_range = street_data['Latitude'].max() - street_data['Latitude'].min()
    lon_range = street_data['Longitude'].max() - street_data['Longitude'].min()
    
    # Determine zoom level based on street span
    max_range = max(lat_range, lon_range)
    if max_range > 2:
        zoom_level = 11
    elif max_range > 0.5:
        zoom_level = 12
    elif max_range > 0.2:
        zoom_level = 13
    else:
        zoom_level = 14
    
    # Create map centered on street
    street_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )
    
    # Extract coordinates for heatmap
    heat_data = []
    for idx, row in street_data.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            heat_data.append([row['Latitude'], row['Longitude']])
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=18,
        radius=10,
        blur=15,
        gradient={0.2: 'blue', 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
    ).add_to(street_map)
    
    # Create URL-safe filename
    street_slug = street_name.lower().replace(' ', '-')
    output_file = os.path.join(output_dir, f'heatmap-street-{street_slug}.html')
    street_map.save(output_file)
    
    print(f"  → Saved to: heatmap-street-{street_slug}.html")

print("\n" + "="*70)
print("✓ All street heatmaps generated successfully!")
print("="*70)
