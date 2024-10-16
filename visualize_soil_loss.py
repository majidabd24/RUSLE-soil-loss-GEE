#to visulise the soil loss

import os
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from shapely.geometry import Point
import pyproj
import pandas as pd
import rasterio
import matplotlib.colors as mcolors
import matplotlib_scalebar.scalebar as sb

# Set the PROJ_LIB environment variable to the correct path
os.environ['PROJ_LIB'] = r'C:\Users\Majid Abdalla\miniconda3\envs\gis_env\Library\share\proj'

# Template function for map production
def create_soil_loss_map(shapefile_path, output_name="Soil_Loss_Map", title="Soil Loss Map"):
    # Load base shapefiles
    azb = gpd.read_file("AZB.shp")           # Amman-Zarqa Basin shapefile
    ktd = gpd.read_file("ktd.shp")           # King Talal Dam reservoir shapefile
    ktd_rivers = gpd.read_file("ktd_rivers.shp")  # Rivers shapefile
    jor_adm0 = gpd.read_file("JOR_adm0.shp")     # Jordan Admin0 shapefile (country borders)

    # Reproject shapefiles to match the CRS of the reservoir
    azb = azb.to_crs(ktd.crs)
    ktd_rivers = ktd_rivers.to_crs(ktd.crs)
    jor_adm0 = jor_adm0.to_crs(ktd.crs)

    # Load the soil loss shapefile
    soil_loss = gpd.read_file(shapefile_path)
    soil_loss = soil_loss.to_crs(ktd.crs)  # Reproject to match KTD CRS

    # Create a 10 km buffer around the KTD reservoir (study area)
    buffer_distance = 10000  # 10 km
    offset_distance = buffer_distance * 0.95  # Shift the buffer towards the right (upstream)
    study_area = ktd.buffer(buffer_distance, cap_style=2).translate(xoff=offset_distance, yoff=0)

    # Create the figure with constrained_layout to avoid tight_layout warning
    fig, ax_main = plt.subplots(figsize=(10, 10), constrained_layout=True)

    # Plot the base layers (vector)
    study_area.plot(ax=ax_main, color='none', edgecolor='purple', linewidth=2, linestyle='--')
    ktd_rivers.plot(ax=ax_main, color='blue', linewidth=1)
    ktd.plot(ax=ax_main, color='lightblue', edgecolor='black', zorder=3)

    # Add King Talal Dam location
    ktd_location = gpd.GeoSeries([Point(35.801389, 32.1900)], crs="EPSG:4326")  # Lon, Lat of King Talal Dam
    ktd_location = ktd_location.to_crs(ktd.crs)
    ktd_location.plot(ax=ax_main, color='red', marker='*', markersize=100, label='King Talal Dam', zorder=4)

    # Convert coordinates to floats for labeling
    x_coord = float(ktd_location.geometry.x.iloc[0])
    y_coord = float(ktd_location.geometry.y.iloc[0])
    ax_main.text(x_coord, y_coord + 500, 'King Talal Dam', fontsize=12, color='black', ha='center')

    # Zoom to the study area
    ax_main.set_xlim(study_area.total_bounds[0] - 1000, study_area.total_bounds[2] + 1000)
    ax_main.set_ylim(study_area.total_bounds[1] - 1000, study_area.total_bounds[3] + 1000)
    ax_main.set_title(title)

    # --- Soil Loss Vector Plot ---
    # Define a color map based on the DN field
    cmap = mcolors.ListedColormap(['#12ff50', '#e5ff12', '#ff4812', '#e6194b', '#800000'])  # Colors for DN 1-5
    soil_loss.plot(column='DN', cmap=cmap, linewidth=0.8, edgecolor='k', legend=False, ax=ax_main, zorder=0)

    # Add a scale bar
    scalebar = sb.ScaleBar(1, location='lower left', scale_loc='bottom', box_alpha=0.6, units='m', length_fraction=0.2)
    ax_main.add_artist(scalebar)

    # --- Overview Map (Inset) ---
    ax_overview = fig.add_axes([0.7, 0.65, 0.25, 0.25], alpha=0.65)
    jor_adm0.plot(ax=ax_overview, color='none', edgecolor='grey', linewidth=1)
    azb.plot(ax=ax_overview, color='none', edgecolor='black', linewidth=1)
    ktd_rivers.plot(ax=ax_overview, color='blue', linewidth=1)
    ktd.plot(ax=ax_overview, color='lightblue', edgecolor='black')

    # Add a red rectangle to indicate KTD location
    ktd_bounds = ktd.total_bounds
    rect = Rectangle((ktd_bounds[0], ktd_bounds[1]), ktd_bounds[2] - ktd_bounds[0], ktd_bounds[3] - ktd_bounds[1],
                     linewidth=2, edgecolor='red', facecolor='none')
    ax_overview.add_patch(rect)

    # Add cities to the overview map
    cities_data = {
        "City": ["Amman", "Irbid", "Aqaba"],
        "Latitude": [31.951569, 32.556778, 29.52667],
        "Longitude": [35.923963, 35.846848, 35.00778]
    }

    # Convert to GeoDataFrame
    cities_df = pd.DataFrame(cities_data)
    cities_gdf = gpd.GeoDataFrame(cities_df, geometry=gpd.points_from_xy(cities_df["Longitude"], cities_df["Latitude"]))
    cities_gdf.set_crs("EPSG:4326", inplace=True)  # Set to WGS84
    cities_gdf = cities_gdf.to_crs(ktd.crs)  # Reproject to match KTD CRS

    # Plot cities on the overview map
    cities_gdf.plot(ax=ax_overview, color='red', markersize=50, label="Cities")

    # Adjust the position of the city labels
    for x, y, label in zip(cities_gdf.geometry.x, cities_gdf.geometry.y, cities_gdf["City"]):
        ax_overview.text(float(x) + 10000, float(y) - 5000, label, fontsize=10, ha='left', color='black')

    ax_overview.text(0.3, 0.4, 'Jordan', transform=ax_overview.transAxes, fontsize=12, ha='center', va='center')
    ax_overview.set_xlim(jor_adm0.total_bounds[0], jor_adm0.total_bounds[2])
    ax_overview.set_ylim(jor_adm0.total_bounds[1], jor_adm0.total_bounds[3])
    ax_overview.set_aspect('equal')
    ax_overview.grid(False)
    ax_overview.set_xticks([])
    ax_overview.set_yticks([])

    # --- Legend ---
    legend_elements = [
        Patch(facecolor='#12ff50', edgecolor='black', label='Slight (<10 tonnes/ha/year)'),
        Patch(facecolor='#e5ff12', edgecolor='black', label='Moderate (10-40 tonnes/ha/year)'),
        Patch(facecolor='#ff4812', edgecolor='black', label='High (40-70 tonnes/ha/year)'),
        Patch(facecolor='#e6194b', edgecolor='black', label='Very High (70-100 tonnes/ha/year)'),
        Patch(facecolor='#800000', edgecolor='black', label='Severe (>100 tonnes/ha/year)'),
    ]
    ax_main.legend(handles=legend_elements, loc='lower right')

    # Save and show the plot
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, f"{output_name}.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

# Example usage for the soil loss map with vector shapefile
create_soil_loss_map("soil_loss.shp", output_name="Soil_Loss_Vector_Map", title="Soil Loss Map of Amman-Zarqa Basin")
