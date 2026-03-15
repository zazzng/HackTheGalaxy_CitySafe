import pandas as pd
import folium
from folium.plugins import HeatMap
import os

# Read the CSV file
df = pd.read_csv('/Users/jana/Documents/HackTheGalaxy_CitySafe/data/raw/icbc_crash_data_cleaned.csv')

# Define zones with their boundaries and center coordinates
zones = {
    'LOWER MAINLAND': {
        'lat': 49.28,
        'lon': -122.78,
        'zoom': 11,
        'bounds': {'north': 50.0, 'south': 48.5, 'east': -121.5, 'west': -124.0}
    },
    'SOUTHERN INTERIOR': {
        'lat': 49.25,
        'lon': -120.30,
        'zoom': 8,
        'bounds': {'north': 50.5, 'south': 48.0, 'east': -119.0, 'west': -121.5}
    },
    'VANCOUVER ISLAND': {
        'lat': 49.15,
        'lon': -123.95,
        'zoom': 8,
        'bounds': {'north': 50.5, 'south': 48.0, 'east': -123.0, 'west': -124.5}
    },
    'NORTH CENTRAL': {
        'lat': 53.90,
        'lon': -122.30,
        'zoom': 8,
        'bounds': {'north': 55.5, 'south': 52.3, 'east': -120.0, 'west': -124.5}
    }
}

output_dir = '/Users/jana/Documents/HackTheGalaxy_CitySafe/output'

for zone_name, zone_info in zones.items():
    print(f"\nGenerating heatmap for {zone_name}...")
    
    # Filter data for this zone
    zone_data = df[df['Region'] == zone_name].copy()
    
    # Get valid coordinates
    zone_data = zone_data.dropna(subset=['Latitude', 'Longitude'])
    zone_data = zone_data[(zone_data['Latitude'] != 0) & (zone_data['Longitude'] != 0)]
    
    if len(zone_data) == 0:
        print(f"  No data found for {zone_name}")
        continue
    
    print(f"  Processing {len(zone_data):,} crash points...")
    
    # Extract coordinates
    heat_data = []
    for idx, row in zone_data.iterrows():
        if pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            heat_data.append([row['Latitude'], row['Longitude']])
    
    if not heat_data:
        print(f"  No valid coordinates for {zone_name}")
        continue
    
    # Create map centered on zone
    zone_map = folium.Map(
        location=[zone_info['lat'], zone_info['lon']],
        zoom_start=zone_info['zoom'],
        tiles='OpenStreetMap'
    )
    
    # Add heatmap layer
    HeatMap(
        heat_data,
        min_opacity=0.2,
        max_zoom=18,
        radius=15,
        blur=15,
        gradient={0.2: 'blue', 0.4: 'green', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'}
    ).add_to(zone_map)
    
    # Save the map
    zone_slug = zone_name.lower().replace(' ', '-')
    output_file = os.path.join(output_dir, f'heatmap-{zone_slug}.html')
    zone_map.save(output_file)
    
    print(f"  ✓ Saved to: heatmap-{zone_slug}.html ({len(zone_data):,} points)")

print("\n" + "="*60)
print("✓ All zoomed heatmaps generated successfully!")
print("="*60)
