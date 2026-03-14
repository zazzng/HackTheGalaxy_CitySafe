import pandas as pd
import folium
from folium.plugins import HeatMap
import json
import os

# Read the CSV file and top cities data
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

with open('/Users/jana/Documents/HackTheGalaxy_CitySafe/output/top_cities.json') as f:
    top_cities_list = json.load(f)

output_dir = '/Users/jana/Documents/HackTheGalaxy_CitySafe/output'

print("Generating city-specific heatmaps...\n")

for city_info in top_cities_list:
    city_name = city_info['city']
    print(f"Processing {city_name}...")
    
    # Filter data for this city
    city_data = df[df['Municipality Name (ifnull)'] == city_name].copy()
    
    # Get valid coordinates
    city_data = city_data.dropna(subset=['Latitude', 'Longitude'])
    city_data = city_data[(city_data['Latitude'] != 0) & (city_data['Longitude'] != 0)]
    
    if len(city_data) == 0:
        print(f"  ⚠️  No coordinates found for {city_name}")
        continue
    
    print(f"  ✓ Found {len(city_data):,} crash points")
    
    # Calculate center and bounds
    center_lat = city_data['Latitude'].mean()
    center_lon = city_data['Longitude'].mean()
    
    # Calculate boundaries
    lat_range = city_data['Latitude'].max() - city_data['Latitude'].min()
    lon_range = city_data['Longitude'].max() - city_data['Longitude'].min()
    
    # Add 20% padding to boundaries
    lat_padding = lat_range * 0.2
    lon_padding = lon_range * 0.2
    
    # Determine zoom level based on city size
    max_range = max(lat_range, lon_range)
    if max_range > 0.5:
        zoom_level = 11
    elif max_range > 0.2:
        zoom_level = 12
    else:
        zoom_level = 13
    
    # Create map centered on city
    city_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_level,
        tiles='OpenStreetMap'
    )
    
    # Extract coordinates for heatmap
    heat_data = []
    for idx, row in city_data.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            heat_data.append([row['Latitude'], row['Longitude']])
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=18,
        radius=12,
        blur=15,
        gradient={0.2: 'blue', 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
    ).add_to(city_map)
    
    # Add city marker at center
    folium.Marker(
        location=[center_lat, center_lon],
        popup=f"<b>{city_name}</b><br>{len(city_data):,} crashes",
        icon=folium.Icon(color='darkblue', icon='info-sign', prefix='glyphicon')
    ).add_to(city_map)
    
    # Create URL-safe filename
    city_slug = city_name.lower().replace(' ', '-')
    output_file = os.path.join(output_dir, f'heatmap-city-{city_slug}.html')
    city_map.save(output_file)
    
    print(f"  → Saved to: heatmap-city-{city_slug}.html")

print("\n" + "="*70)
print("✓ All city heatmaps generated successfully!")
print("="*70)
