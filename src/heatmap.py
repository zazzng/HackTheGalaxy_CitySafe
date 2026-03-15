import pandas as pd
import folium
from folium.plugins import HeatMap
import json

# ============================================================
# STEP 1: LOADING THE DATA
# ============================================================
print("Loading CSV file...")
data = pd.read_csv('data/raw/icbc_crash_data_cleaned.csv')
HOTSPOT_LIMIT = 20

print(f"Dataset shape: {data.shape}")

# Keep only rows with valid coordinates for any map/hotspot logic.
valid_location_rows = data.dropna(subset=['Latitude', 'Longitude']).copy()
valid_location_rows['Latitude'] = pd.to_numeric(valid_location_rows['Latitude'], errors='coerce')
valid_location_rows['Longitude'] = pd.to_numeric(valid_location_rows['Longitude'], errors='coerce')
valid_location_rows = valid_location_rows.dropna(subset=['Latitude', 'Longitude'])
valid_location_rows = valid_location_rows[
    (valid_location_rows['Latitude'] != 0) & (valid_location_rows['Longitude'] != 0)
]

# Remove unknown/blank municipality rows so they never appear in hotspots.
municipality_col = 'Municipality Name (ifnull)'
valid_location_rows[municipality_col] = valid_location_rows[municipality_col].astype(str).str.strip()
valid_location_rows = valid_location_rows[
    valid_location_rows[municipality_col].ne('')
    & ~valid_location_rows[municipality_col].str.lower().isin({'unknown', 'unk', 'nan', 'none', 'null'})
]

# Extract crash points for the heatmap layer.
crashes = valid_location_rows[['Latitude', 'Longitude']]

print(f"Total valid crashes: {len(crashes)}")
print(f"Rows after removing unknown municipality: {len(valid_location_rows)}")

# Calculate map center
center_lat = crashes['Latitude'].mean()
center_lon = crashes['Longitude'].mean()
print(f"Map center: ({center_lat:.5f}, {center_lon:.5f})")

# ============================================================
# MODE 1: HEATMAP - Shows density of all crashes
# ============================================================
print("\n" + "="*60)
print("MODE 1: Creating HEATMAP (showing crash density)...")
print("="*60)

crash_map_heat = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='OpenStreetMap'
)

# Add heatmap layer with all crashes
print("Adding heatmap layer with all crashes...")
heatmap_points = crashes.values.tolist()
HeatMap(
    heatmap_points,
    name='All Crashes',
    radius=15,
    blur=12,
    max_zoom=1,
    gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'yellow', 0.8: 'orange', 1.0: 'red'},
    min_opacity=0.5,
    max_opacity=0.95
).add_to(crash_map_heat)

folium.LayerControl().add_to(crash_map_heat)

# Save MODE 1
output_heat = 'output/heatmap.html'
crash_map_heat.save(output_heat)
print(f"✓ Heatmap (density view) saved!")

# ============================================================
# MODE 2: MARKERS - Shows top 20 crash hotspots
# ============================================================
print("\n" + "="*60)
print("MODE 2: Creating MARKERS (top 20 hotspots)...")
print("="*60)

# Find top 20 hotspots from valid coordinates only
crashes_by_location = (
    valid_location_rows
    .groupby(['Latitude', 'Longitude', 'Municipality Name (ifnull)'])['Total Crashes']
    .sum()
    .sort_values(ascending=False)
)

top_hotspots = []
for i, (coords, count) in enumerate(crashes_by_location.head(HOTSPOT_LIMIT).items()):
    lat, lng, city = coords
    city_clean = str(city).strip().title()
    top_hotspots.append({
        'lat': lat,
        'lng': lng,
        'city': city_clean,
        'name': city_clean,
        'crashes': int(count),
        'rank': i + 1
    })

print(f"Top {HOTSPOT_LIMIT} hotspots found: {len(top_hotspots)}")
for spot in top_hotspots[:10]:
    print(f"  #{spot['rank']}: {spot['city']} - LAT {spot['lat']:.5f}, LNG {spot['lng']:.5f} - {spot['crashes']} crashes")

# Create markers map
crash_map_markers = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles='OpenStreetMap'
)

# Add markers for top 20
print("\nAdding markers for top 20 hotspots...")
for hotspot in top_hotspots:
    # Determine color based on rank/crashes
    if hotspot['crashes'] > 1500:
        color = 'darkred'
    elif hotspot['crashes'] > 1000:
        color = 'red'
    elif hotspot['crashes'] > 800:
        color = 'orange'
    else:
        color = 'yellow'
    
    popup_html = f"""
    <div style="font-family: Arial; width: 250px;">
        <h4 style="margin: 5px 0; color: #d32f2f;">🔴 Hotspot #{hotspot['rank']}</h4>
        <hr style="margin: 5px 0;">
        <p style="margin: 3px 0;"><b>City:</b> {hotspot['city']}</p>
        <p style="margin: 3px 0;"><b>Latitude:</b> <code style="background: #f0f0f0; padding: 2px 5px;">{hotspot['lat']:.5f}</code></p>
        <p style="margin: 3px 0;"><b>Longitude:</b> <code style="background: #f0f0f0; padding: 2px 5px;">{hotspot['lng']:.5f}</code></p>
        <p style="margin: 3px 0;"><b>Crashes:</b> <b style="color: red;">{hotspot['crashes']:,}</b></p>
    </div>
    """
    
    folium.Marker(
        location=[hotspot['lat'], hotspot['lng']],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color, icon='exclamation', prefix='fa'),
        tooltip=f"#{hotspot['rank']}: {hotspot['city']} - {hotspot['crashes']} crashes"
    ).add_to(crash_map_markers)

folium.LayerControl().add_to(crash_map_markers)

# Save MODE 2
output_markers = 'output/heatmap-markers.html'
crash_map_markers.save(output_markers)
print(f"✓ Markers (top 20) saved!")

# Save shared hotspot data for warning detection (single source of truth).
output_hotspots = 'output/hotspots.json'
with open(output_hotspots, 'w', encoding='utf-8') as f:
    json.dump(top_hotspots, f, ensure_ascii=True, indent=2)
print(f"✓ Hotspot data saved: {output_hotspots}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("✓ COMPLETE!")
print("="*60)
print(f"\n📍 Two modes created:")
print(f"\n1️⃣  HEATMAP MODE (Density):")
print(f"   File: heatmap.html")
print(f"   Shows: ALL {len(crashes):,} crash locations as heat")
print(f"   Use for: Seeing overall crash density patterns")
print(f"\n2️⃣  MARKER MODE (Top 20):")
print(f"   File: heatmap-markers.html")
print(f"   Shows: Top 20 crash hotspots with exact coordinates")
print(f"   Use for: Warning detection on specific locations")
print(f"\n💡 Tip: Add a toggle button in interactive-warning.html to switch between modes!")
