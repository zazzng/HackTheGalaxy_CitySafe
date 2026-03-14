import pandas as pd
import folium
from folium.plugins import HeatMap

# ============================================================
# STEP 1: LOADING THE DATA
# ============================================================
print("Loading CSV file...")
data = pd.read_csv('data/raw/icbc_crash_data_cleaned.csv')

# Preview the first 5 rows of the dataset
print(data.head())
print(f"\nDataset shape: {data.shape}")

# ============================================================
# STEP 2: PREPARING DATA FOR HEATMAP
# ============================================================
print("\nPreparing data for heatmap...")

# Extract latitude and longitude columns
lat_col = 'Latitude'
lon_col = 'Longitude'

# Extract and remove rows with missing coordinates
heatmap_data = data[[lat_col, lon_col]].dropna()

# Convert to list format required by folium heatmaps
# Format: [[lat, lon], [lat, lon], ...]
heatmap_points = heatmap_data.values.tolist()

print(f"Total crash points: {len(heatmap_points)}")
print(f"Sample points: {heatmap_points[:3]}")

# ============================================================
# STEP 3: CREATING THE MAP
# ============================================================
print("\nCreating folium map...")

# Calculate the center of the map using mean latitude and longitude
center_lat = heatmap_data[lat_col].mean()
center_lon = heatmap_data[lon_col].mean()
print(f"Map center: ({center_lat}, {center_lon})")

# Create a folium map centered at the calculated coordinates
crash_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=12,
    tiles='OpenStreetMap'
)

# Add HeatMap layer
HeatMap(
    heatmap_points,
    radius=15,
    blur=25,
    max_zoom=1
).add_to(crash_map)

# ============================================================
# STEP 4: SAVING THE HEATMAP
# ============================================================
print("\nSaving heatmap...")

# Export the map as an HTML file
output_path = 'output/heatmap.html'
crash_map.save(output_path)
print(f"Heatmap saved to: {output_path}")
print("\n✓ Done! Open the generated heatmap.html in your browser to view the crash hotspots.")
