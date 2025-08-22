#!/usr/bin/env python3
"""
Composite Figure 1: Global Distribution and Temporal Patterns of Urban Sunset Precipitation
This script generates a publication-quality composite figure combining:
- Global map showing city-level enhancement/suppression
- Temporal comparison of urban vs rural precipitation
- Urban-only precipitation events
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
from matplotlib.colors import ListedColormap
import contextily as ctx
import warnings
warnings.filterwarnings('ignore')

# ===================== Configuration =====================

# Color scheme (colorblind-friendly)
COLORS = {
    'urban': '#D32F2F',       # Red for urban
    'rural': '#B8860B',       # Dark goldenrod for rural  
    'urban_only': '#2E8B57',  # Sea green for urban-only
    'enhance_strong': (255/255, 120/255, 130/255),  # Strong suppression (red)
    'enhance_weak': (255/255, 179/255, 186/255),    # Weak suppression (pink)
    'suppress_weak': (180/255, 210/255, 100/255),   # Weak enhancement (light green)
    'suppress_strong': (120/255, 200/255, 150/255)  # Strong enhancement (green)
}

# Figure dimensions (Nature format)
FIG_WIDTH = 18  # cm
FIG_HEIGHT = 7  # cm
DPI = 300

# Font settings
FONT_SIZE = {
    'panel_label': 12,
    'axis_label': 10,
    'tick_label': 9,
    'legend': 9,
    'annotation': 10
}

# ===================== Data Loading Functions =====================

def load_temporal_data(data_dir='data/'):
    """Load preprocessed temporal data from .npy files"""
    
    data = {}
    
    # Urban vs Rural comparison (0.2-0.5 mm/hr)
    data['urban_mean'] = np.load(f"{data_dir}/urban_02_05_mean.npy")
    data['urban_low'] = np.load(f"{data_dir}/urban_02_05_low.npy")
    data['urban_high'] = np.load(f"{data_dir}/urban_02_05_high.npy")
    
    data['rural_mean'] = np.load(f"{data_dir}/rural_02_05_mean.npy")
    data['rural_low'] = np.load(f"{data_dir}/rural_02_05_low.npy")
    data['rural_high'] = np.load(f"{data_dir}/rural_02_05_high.npy")
    
    # Urban-only events (0.2-0.5 mm/hr)
    data['turban_mean'] = np.load(f"{data_dir}/turban_02_05_mean.npy")
    data['turban_low'] = np.load(f"{data_dir}/turban_02_05_low.npy")
    data['turban_high'] = np.load(f"{data_dir}/turban_02_05_high.npy")
    
    return data

def load_spatial_data(year=2020, data_dir='data/'):
    """Load spatial data for global map"""
    
    filename = f"{data_dir}/spa_{year}.txt"
    data = np.loadtxt(filename)
    
    # Columns: lat, lon, difference_index
    return data

# ===================== Plotting Functions =====================

def plot_global_map(ax, spatial_data):
    """Plot global distribution map (Panel a)"""
    
    # Sort by difference index for proper layering
    spatial_data = spatial_data[spatial_data[:, 2].argsort()]
    
    # Assign colors based on thresholds
    colors = []
    enhancement_count = 0
    total_cities = len(spatial_data)
    
    for value in spatial_data[:, 2]:
        if value < -0.1:
            colors.append(COLORS['enhance_strong'])
        elif value < 0:
            colors.append(COLORS['enhance_weak'])
        elif value < 0.1:
            colors.append(COLORS['suppress_weak'])
            enhancement_count += 1
        else:
            colors.append(COLORS['suppress_strong'])
            enhancement_count += 1
    
    # Calculate percentage
    enhancement_pct = (enhancement_count / total_cities) * 100
    
    # Create GeoDataFrame
    df = pd.DataFrame(spatial_data, columns=["lat", "lon", "value"])
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.lon, df.lat),
        crs="EPSG:4326"
    ).to_crs(epsg=3857)
    
    # Plot points
    gdf.plot(ax=ax, markersize=3, c=colors, alpha=0.8)
    
    # Add basemap
    ctx.add_basemap(
        ax=ax,
        source=ctx.providers.CartoDB.PositronNoLabels,
        attribution=""
    )
    
    # Set extent and labels
    ax.set_xlim(-18000000, 18000000)
    ax.set_ylim(-8000000, 9000000)
    ax.set_xticks([-18000000, -9000000, 0, 9000000, 18000000])
    ax.set_xticklabels(['-180°', '-90°', '0°', '90°', '180°'], fontsize=FONT_SIZE['tick_label'])
    ax.set_yticks([-6000000, -3000000, 0, 3000000, 6000000])
    ax.set_yticklabels(['-60°', '-30°', '0°', '30°', '60°'], fontsize=FONT_SIZE['tick_label'])
    
    # Add title and annotation
    ax.set_title('Global Distribution', fontsize=FONT_SIZE['axis_label'], pad=10)
    
    # Add enhancement percentage
    ax.text(0.02, 0.95, f'{enhancement_pct:.1f}% of cities\nshow enhancement',
            transform=ax.transAxes, fontsize=FONT_SIZE['annotation'],
            fontweight='bold', va='top', ha='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Add mini colorbar/legend
    add_map_legend(ax)
    
    return ax

def add_map_legend(ax):
    """Add a compact legend to the map"""
    
    from matplotlib.patches import Rectangle
    
    # Legend items
    legend_elements = [
        Rectangle((0, 0), 1, 1, fc=COLORS['enhance_strong'], label='< -10%'),
        Rectangle((0, 0), 1, 1, fc=COLORS['enhance_weak'], label='-10% to 0%'),
        Rectangle((0, 0), 1, 1, fc=COLORS['suppress_weak'], label='0% to 10%'),
        Rectangle((0, 0), 1, 1, fc=COLORS['suppress_strong'], label='> 10%')
    ]
    
    legend = ax.legend(handles=legend_elements, 
                      loc='lower right',
                      title='Urban Impact',
                      fontsize=FONT_SIZE['legend'],
                      title_fontsize=FONT_SIZE['legend'],
                      frameon=True,
                      fancybox=True,
                      framealpha=0.9)
    
    return legend

def plot_temporal_comparison(ax, data):
    """Plot urban vs rural temporal comparison (Panel b)"""
    
    x = np.arange(1000)
    
    # Plot lines
    ax.plot(x, data['urban_mean'], color=COLORS['urban'], 
            linewidth=1.5, label='Urban Area', alpha=0.9)
    ax.plot(x, data['rural_mean'], color=COLORS['rural'], 
            linewidth=1.5, label='Rural Area', alpha=0.9)
    
    # Add confidence intervals
    ax.fill_between(x, data['urban_low'], data['urban_high'], 
                    color=COLORS['urban'], alpha=0.2)
    ax.fill_between(x, data['rural_low'], data['rural_high'], 
                    color=COLORS['rural'], alpha=0.2)
    
    # Mark sunset
    ax.axvline(856, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(856, ax.get_ylim()[1]*0.95, 'Sunset', 
            ha='center', fontsize=FONT_SIZE['annotation'], fontweight='bold')
    
    # Set labels and ticks
    ax.set_xticks([143, 856])
    ax.set_xticklabels(['Midday', ''], fontsize=FONT_SIZE['tick_label'])
    ax.set_ylabel('Count of wet hour', fontsize=FONT_SIZE['axis_label'])
    ax.set_ylim(6.8, 9.8)
    ax.set_yticks([7, 8, 9])
    
    # Title and legend
    ax.set_title('Light Precipitation (0.2-0.5 mm/hr)', 
                fontsize=FONT_SIZE['axis_label'], pad=10)
    ax.legend(loc='upper left', fontsize=FONT_SIZE['legend'], frameon=False)
    
    # Highlight sunset peak
    sunset_idx = 856
    urban_sunset = data['urban_mean'][sunset_idx]
    ax.plot(sunset_idx, urban_sunset, 'o', color=COLORS['urban'], 
            markersize=6, markeredgecolor='white', markeredgewidth=1)
    
    return ax

def plot_urban_only(ax, data):
    """Plot urban-only precipitation events (Panel c)"""
    
    x = np.arange(1000)
    
    # Plot line
    ax.plot(x, data['turban_mean'], color=COLORS['urban_only'], 
            linewidth=1.5, label='Precipitation only\nin Urban Area', alpha=0.9)
    
    # Add confidence interval
    ax.fill_between(x, data['turban_low'], data['turban_high'], 
                    color=COLORS['urban_only'], alpha=0.2)
    
    # Mark sunset
    ax.axvline(856, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.text(856, ax.get_ylim()[1]*0.95, 'Sunset', 
            ha='center', fontsize=FONT_SIZE['annotation'], fontweight='bold')
    
    # Mark peaks
    # Find midday peak (around index 400-500)
    midday_peak_idx = np.argmax(data['turban_mean'][400:500]) + 400
    sunset_peak_idx = 856
    
    ax.plot(midday_peak_idx, data['turban_mean'][midday_peak_idx], 'o', 
            color=COLORS['urban_only'], markersize=6, 
            markeredgecolor='white', markeredgewidth=1)
    ax.plot(sunset_peak_idx, data['turban_mean'][sunset_peak_idx], 'o', 
            color=COLORS['urban_only'], markersize=6, 
            markeredgecolor='white', markeredgewidth=1)
    
    # Set labels and ticks
    ax.set_xticks([143, 856])
    ax.set_xticklabels(['Midday', ''], fontsize=FONT_SIZE['tick_label'])
    ax.set_ylabel('Count of wet hour', fontsize=FONT_SIZE['axis_label'])
    ax.set_ylim(2.8, 4.2)
    ax.set_yticks([3.0, 3.5, 4.0])
    
    # Title and legend
    ax.set_title('Urban-Specific Events', 
                fontsize=FONT_SIZE['axis_label'], pad=10)
    ax.legend(loc='upper left', fontsize=FONT_SIZE['legend'], frameon=False)
    
    return ax

# ===================== Main Function =====================

def create_composite_figure(output_path='figures/figure1_composite.pdf'):
    """Create the complete composite figure"""
    
    print("Loading data...")
    temporal_data = load_temporal_data()
    spatial_data = load_spatial_data(year=2020)
    
    print("Creating figure...")
    # Convert cm to inches for matplotlib
    fig = plt.figure(figsize=(FIG_WIDTH/2.54, FIG_HEIGHT/2.54))
    
    # Create gridspec with custom width ratios
    gs = gridspec.GridSpec(1, 3, width_ratios=[4, 3, 3], 
                          wspace=0.35, left=0.06, right=0.98,
                          bottom=0.15, top=0.85)
    
    # Create subplots
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])
    
    print("Plotting global map...")
    plot_global_map(ax1, spatial_data)
    
    print("Plotting temporal comparison...")
    plot_temporal_comparison(ax2, temporal_data)
    
    print("Plotting urban-only events...")
    plot_urban_only(ax3, temporal_data)
    
    # Add panel labels
    for ax, label in zip([ax1, ax2, ax3], ['a', 'b', 'c']):
        ax.text(0.02, 0.98, label, transform=ax.transAxes,
                fontsize=FONT_SIZE['panel_label'], fontweight='bold', 
                va='top', ha='left')
    
    # Save figure
    print(f"Saving figure to {output_path}...")
    plt.savefig(output_path, dpi=DPI, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    
    # Also save as PNG for quick viewing
    png_path = output_path.replace('.pdf', '.png')
    plt.savefig(png_path, dpi=DPI, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    
    print(f"Figure saved successfully!")
    print(f"PDF: {output_path}")
    print(f"PNG: {png_path}")
    
    plt.show()
    
    return fig

# ===================== Execute =====================

if __name__ == "__main__":
    # Create the composite figure
    fig = create_composite_figure()