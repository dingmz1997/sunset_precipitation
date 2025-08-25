"""
Figure 1 Component Functions for Urban Sunset Precipitation Analysis
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from matplotlib.patches import Rectangle


# ========== Color Definitions for Temporal Plots ==========
# Define colors as variables for easy modification
TEMPORAL_ENHANCEMENT_COLOR = "#FF6B35"  # Orange/coral for enhancement percentage
TEMPORAL_CITIES_COLOR = "#4A90E2"       # Light blue for number of cities


# ========== Component 1: Global Map Functions ==========


def create_global_map_only(
    ax,
    spatial_2020,
    COLORS,
    show_enhancement_text=False,
    legend_position="lower right",
    legend_fontsize=8,
    legend_markerscale=1.0,
    legend_columnspacing=1.0,
    aspect="auto",
):
    """
    Create just the global distribution map without temporal inset

    Parameters:
    -----------
    ax : matplotlib axis
        The axis to plot on
    spatial_2020 : array
        2020 spatial data with columns [lat, lon, value]
    COLORS : dict
        Color scheme dictionary
    show_enhancement_text : bool, optional
        Whether to show the enhancement percentage annotation (default: False)
    legend_position : str or tuple, optional
        Legend position. Can be:
        - String: 'lower right', 'upper left', etc.
        - Tuple: (x, y) as fraction of axes (0-1), e.g., (0.7, 0.2) for 70% right, 20% up
    legend_fontsize : int, optional
        Font size for legend text (default: 8)
    legend_markerscale : float, optional
        Scale factor for legend markers (default: 1.0)
    legend_columnspacing : float, optional
        Spacing between legend columns if using ncol (default: 1.0)
    aspect : str or float, optional
        Aspect ratio setting: 'auto' for flexible, 'equal' for fixed, or a numeric value (default: 'auto')

    Returns:
    --------
    enhancement_pct : float
        Percentage of cities showing enhancement
    """
    # Sort and color spatial data
    spatial_2020_sorted = spatial_2020[spatial_2020[:, 2].argsort()]
    colors = []
    enhancement_count = 0

    for value in spatial_2020_sorted[:, 2]:
        if value < -0.1:
            colors.append(COLORS["enhance_strong"])
        elif value < 0:
            colors.append(COLORS["enhance_weak"])
        elif value < 0.1:
            colors.append(COLORS["suppress_weak"])
            enhancement_count += 1
        else:
            colors.append(COLORS["suppress_strong"])
            enhancement_count += 1

    enhancement_pct = (enhancement_count / len(spatial_2020)) * 100

    # Create GeoDataFrame and plot
    df = pd.DataFrame(spatial_2020_sorted, columns=["lat", "lon", "value"])
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326").to_crs(
        epsg=3857
    )

    gdf.plot(ax=ax, markersize=20, c=colors, alpha=0.8)
    ctx.add_basemap(ax, source=ctx.providers.CartoDB.PositronNoLabels, attribution="")

    # Configure map
    ax.set_xlim(-18000000, 18000000)
    ax.set_ylim(-8000000, 9000000)

    # Set aspect ratio
    ax.set_aspect(aspect)
    ax.set_xticks([-18000000, -9000000, 0, 9000000, 18000000])
    ax.set_xticklabels(["-180°", "-90°", "0°", "90°", "180°"], fontsize=9)
    ax.set_yticks([-6000000, -3000000, 0, 3000000, 6000000])
    ax.set_yticklabels(["-60°", "-30°", "0°", "30°", "60°"], fontsize=9)
    ax.set_title("Global Distribution (2020)", fontsize=13, pad=10)

    # Add enhancement annotation (only if requested)
    if show_enhancement_text:
        ax.text(
            0.02,
            0.95,
            f"{enhancement_pct:.1f}% of cities\nshow enhancement",
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            va="top",
            ha="left",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
        )

    # Add legend with customizable size
    # Create smaller rectangles for legend markers if needed
    marker_size = 0.8 * legend_markerscale  # Base size multiplied by scale
    legend_elements = [
        Rectangle((0, 0), marker_size, marker_size, fc=COLORS["enhance_strong"], label="< -10%"),
        Rectangle((0, 0), marker_size, marker_size, fc=COLORS["enhance_weak"], label="-10% to 0%"),
        Rectangle((0, 0), marker_size, marker_size, fc=COLORS["suppress_weak"], label="0% to 10%"),
        Rectangle((0, 0), marker_size, marker_size, fc=COLORS["suppress_strong"], label="> 10%"),
    ]

    # Handle legend position - either string or tuple for custom positioning
    if isinstance(legend_position, tuple):
        # Use bbox_to_anchor for percentage-based positioning
        legend = ax.legend(
            handles=legend_elements,
            bbox_to_anchor=legend_position,
            loc="center",
            title="Urban Impact",
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
            frameon=True,
            framealpha=0.9,
            handlelength=1.0 * legend_markerscale,
            handleheight=1.0 * legend_markerscale,
            columnspacing=legend_columnspacing,
            borderpad=0.3,
            handletextpad=0.5,
            labelspacing=0.3,
        )
    else:
        # Use standard location string
        legend = ax.legend(
            handles=legend_elements,
            loc=legend_position,
            title="Urban Impact",
            fontsize=legend_fontsize,
            title_fontsize=legend_fontsize,
            frameon=True,
            framealpha=0.9,
            handlelength=1.0 * legend_markerscale,
            handleheight=1.0 * legend_markerscale,
            columnspacing=legend_columnspacing,
            borderpad=0.3,
            handletextpad=0.5,
            labelspacing=0.3,
        )

    return enhancement_pct


def create_temporal_stability_inset(
    parent_ax, temporal_stability, position=[0.62, 0.65, 0.35, 0.28]
):
    """
    Create temporal stability inset on a parent axis with dual y-axes

    Parameters:
    -----------
    parent_ax : matplotlib axis
        The parent axis to add the inset to
    temporal_stability : DataFrame
        20-year temporal stability data with columns 'year', 'n_cities', and 'enhancement_pct'
    position : list
        [x, y, width, height] position of inset in axes coordinates

    Returns:
    --------
    inset_ax : matplotlib axis
        The inset axis object (left axis)
    inset_ax2 : matplotlib axis
        The right axis object
    """
    # Create inset
    inset_ax = parent_ax.inset_axes(position)

    # Create second y-axis
    inset_ax2 = inset_ax.twinx()

    # Plot enhancement percentage on left axis
    # inset_ax.fill_between(
    #     temporal_stability["year"],
    #     0,
    #     temporal_stability["enhancement_pct"],
    #     color="#2E8B57",
    #     alpha=0.3,
    # )

    line1 = inset_ax.plot(
        temporal_stability["year"],
        temporal_stability["enhancement_pct"],
        color=TEMPORAL_ENHANCEMENT_COLOR,
        linewidth=1.5,
        marker="o",
        markersize=2,
        label="Enhancement %",
    )

    # Plot number of cities on right axis
    line2 = inset_ax2.plot(
        temporal_stability["year"],
        temporal_stability["n_cities"],
        color=TEMPORAL_CITIES_COLOR,
        linewidth=1.5,
        marker="s",
        markersize=2,
        # linestyle="--",
        label="Number of Cities",
    )

    # Add average line for enhancement
    avg_enhancement = temporal_stability["enhancement_pct"].mean()
    inset_ax.axhline(avg_enhancement, color="black", linestyle="--", linewidth=0.8, alpha=0.7)
    inset_ax.text(
        2002,
        avg_enhancement + 0.5,
        f"{avg_enhancement:.1f}%",
        fontsize=6,
        va="bottom",
        fontweight="bold",
    )

    # Configure left axis (enhancement %)
    inset_ax.set_xlim(2000, 2021)
    inset_ax.set_ylim(55, 70)
    inset_ax.set_xticks([2001, 2010, 2020])
    inset_ax.set_xticklabels(["2001", "2010", "2020"], fontsize=7)
    inset_ax.set_yticks([55, 60, 65, 70])
    inset_ax.set_yticklabels(["55%", "60%", "65%", "70%"], fontsize=7)
    inset_ax.set_ylabel("Enhancement %", fontsize=7, color=TEMPORAL_ENHANCEMENT_COLOR)
    inset_ax.tick_params(axis="y", labelcolor=TEMPORAL_ENHANCEMENT_COLOR)

    # Configure right axis (number of cities)
    inset_ax2.set_ylim(480, 550)
    inset_ax2.set_yticks([480, 500, 520, 540, 560])
    inset_ax2.set_yticklabels(["480", "500", "520", "540", "560"], fontsize=7)
    inset_ax2.set_ylabel("Number of Cities", fontsize=7, color=TEMPORAL_CITIES_COLOR)
    inset_ax2.tick_params(axis="y", labelcolor=TEMPORAL_CITIES_COLOR)

    # Title and grid
    # inset_ax.set_title("20-Year Stability", fontsize=8, fontweight="bold")
    inset_ax.grid(True, alpha=0.3, linewidth=0.5)
    inset_ax.set_facecolor("white")
    inset_ax.patch.set_alpha(0.95)

    # Combined legend
    # lines = line1 + line2
    # labels = [l.get_label() for l in lines]
    # inset_ax.legend(lines, labels, loc="lower left", fontsize=6, frameon=False)

    return inset_ax, inset_ax2


def create_temporal_stability_standalone(
    ax,
    temporal_stability,
    show_stats_box=False,
    stats_position=(0.02, 0.98),
    fontsize=8,
):
    """
    Create standalone temporal stability plot with dual y-axes

    Parameters:
    -----------
    ax : matplotlib axis
        The axis to plot on
    temporal_stability : DataFrame
        20-year temporal stability data with columns 'year', 'n_cities', and 'enhancement_pct'
    show_stats_box : bool, optional
        Whether to show the statistics box (default: True)
    stats_position : tuple, optional
        Position of stats box as (x, y) fraction of axes (default: (0.02, 0.98))
    fontsize : int, optional
        Base font size for the plot (default: 10)

    Returns:
    --------
    ax2 : matplotlib axis
        The second y-axis (for cities count)
    """
    # Create second y-axis
    ax2 = ax.twinx()

    # Plot enhancement percentage on left axis
    ax.fill_between(
        temporal_stability["year"],
        0,
        temporal_stability["enhancement_pct"],
        color=TEMPORAL_ENHANCEMENT_COLOR,
        alpha=0.3,
    )
    line1 = ax.plot(
        temporal_stability["year"],
        temporal_stability["enhancement_pct"],
        color=TEMPORAL_ENHANCEMENT_COLOR,
        linewidth=2,
        marker="o",
        markersize=4,
        label="Enhancement %",
    )

    # Plot number of cities on right axis
    line2 = ax2.plot(
        temporal_stability["year"],
        temporal_stability["n_cities"],
        color=TEMPORAL_CITIES_COLOR,
        linewidth=2,
        marker="s",
        markersize=4,
        linestyle=":",
        label="Number of Cities",
    )

    # # Add average line for enhancement
    avg_enhancement = temporal_stability["enhancement_pct"].mean()
    # ax.axhline(avg_enhancement, color="black", linestyle="--", linewidth=1, alpha=0.7)
    # ax.text(
    #     2020.5,
    #     avg_enhancement,
    #     f"{avg_enhancement:.1f}%",
    #     fontsize=fontsize - 1,
    #     va="center",
    #     fontweight="bold",
    # )

    # Configure left axis (enhancement %)
    ax.set_xlim(2000, 2021)
    ax.set_ylim(55, 70)
    ax.set_xticks([2001, 2005, 2010, 2015, 2020])
    ax.set_xlabel("Year", fontsize=fontsize)
    ax.set_ylabel("Enhancement %", fontsize=fontsize, color=TEMPORAL_ENHANCEMENT_COLOR)
    ax.tick_params(axis="y", labelcolor=TEMPORAL_ENHANCEMENT_COLOR, labelsize=fontsize - 1)
    ax.tick_params(axis="x", labelsize=fontsize - 1)

    # Configure right axis (number of cities)
    ax2.set_ylim(480, 550)
    ax2.set_ylabel("Number of Cities", fontsize=fontsize, color=TEMPORAL_CITIES_COLOR)
    ax2.tick_params(axis="y", labelcolor=TEMPORAL_CITIES_COLOR, labelsize=fontsize - 1)

    # Title and grid
    ax.set_title(
        "20-Year Temporal Stability of Sunset Enhancement", fontsize=fontsize + 1, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)

    # Combined legend
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc="upper right", fontsize=fontsize - 1)

    # Add statistics box if requested
    if show_stats_box:
        std_dev = temporal_stability["enhancement_pct"].std()
        min_val = temporal_stability["enhancement_pct"].min()
        max_val = temporal_stability["enhancement_pct"].max()
        avg_cities = temporal_stability["n_cities"].mean()

        stats_text = f"Enhancement:\n  Mean: {avg_enhancement:.1f}%\n  Std: {std_dev:.1f}%\n  Range: {min_val:.1f}-{max_val:.1f}%\n\nCities:\n  Mean: {avg_cities:.0f}"
        ax.text(
            stats_position[0],
            stats_position[1],
            stats_text,
            transform=ax.transAxes,
            fontsize=fontsize - 3,
            va="top",
            ha="left",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
        )

    return ax2


# ========== Component 2: Urban vs Rural Comparison ==========


def create_urban_rural_comparison(
    ax,
    urban_mean,
    urban_low,
    urban_high,
    rural_mean,
    rural_low,
    rural_high,
    COLORS,
    intensity_label="Light Precipitation (0.2-0.5 mm/hr)",
    y_lim=(6.8, 9.8),
    y_ticks=[7, 8, 9],
    show_legend=True,
    show_title=True,
    show_ylabel=True,
    show_xlabel=True,
):
    """
    Create Panel B: Urban vs Rural comparison plot

    Parameters:
    -----------
    ax : matplotlib axis
        The axis to plot on
    urban_mean, urban_low, urban_high : arrays
        Urban area precipitation data (mean and confidence intervals)
    rural_mean, rural_low, rural_high : arrays
        Rural area precipitation data (mean and confidence intervals)
    COLORS : dict
        Color scheme dictionary
    intensity_label : str, optional
        Title for the intensity range
    y_lim : tuple, optional
        Y-axis limits (min, max)
    y_ticks : list, optional
        Y-axis tick positions
    show_legend : bool, optional
        Whether to show the legend (default: True)
    show_title : bool, optional
        Whether to show the title (default: True)
    show_ylabel : bool, optional
        Whether to show the y-axis label (default: True)
    show_xlabel : bool, optional
        Whether to show the x-axis labels (default: True)
    """

    x = np.arange(1000)

    # Plot lines
    ax.plot(x, urban_mean, color=COLORS["urban"], linewidth=1.5, label="Urban", alpha=0.9)
    ax.plot(x, rural_mean, color=COLORS["rural"], linewidth=1.5, label="Rural", alpha=0.9)

    # Confidence intervals
    ax.fill_between(x, urban_low, urban_high, color=COLORS["urban"], alpha=0.2)
    ax.fill_between(x, rural_low, rural_high, color=COLORS["rural"], alpha=0.2)

    # Mark sunset
    ax.axvline(856, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    # Configure axes
    ax.set_xticks([143, 856])
    if show_xlabel:
        ax.set_xticklabels(["Midday", "Sunset"], fontsize=9)
        labels = ax.get_xticklabels()
        labels[1].set_fontweight("bold")
    else:
        ax.set_xticklabels([])

    if show_ylabel:
        ax.set_ylabel("Count of wet hour", fontsize=10)

    ax.set_ylim(y_lim)
    ax.set_yticks(y_ticks)

    if show_title:
        ax.set_title(intensity_label, fontsize=10, pad=10)

    if show_legend:
        ax.legend(bbox_to_anchor=(0.2, 0.02), loc='lower left', fontsize=9, frameon=False)


# ========== Component 3: Urban-Only Events ==========


def create_urban_only_events(
    ax,
    turban_mean,
    turban_low,
    turban_high,
    COLORS,
    intensity_label="Urban-Specific Events",
    y_lim=(2.8, 4.2),
    y_ticks=[3.0, 3.5, 4.0],
    show_legend=True,
    show_title=True,
    show_ylabel=True,
    show_xlabel=True,
):
    """
    Create Panel C: Urban-only precipitation events

    Parameters:
    -----------
    ax : matplotlib axis
        The axis to plot on
    turban_mean, turban_low, turban_high : arrays
        Urban-only precipitation data (mean and confidence intervals)
    COLORS : dict
        Color scheme dictionary
    intensity_label : str, optional
        Title for the plot
    y_lim : tuple, optional
        Y-axis limits (min, max)
    y_ticks : list, optional
        Y-axis tick positions
    show_legend : bool, optional
        Whether to show the legend (default: True)
    show_title : bool, optional
        Whether to show the title (default: True)
    show_ylabel : bool, optional
        Whether to show the y-axis label (default: True)
    show_xlabel : bool, optional
        Whether to show the x-axis labels (default: True)
    """

    x = np.arange(1000)

    # Plot line
    ax.plot(
        x,
        turban_mean,
        color=COLORS["urban_only"],
        linewidth=1.5,
        label="Urban Only",
        alpha=0.9,
    )

    # Confidence interval
    ax.fill_between(x, turban_low, turban_high, color=COLORS["urban_only"], alpha=0.2)

    # Mark sunset
    ax.axvline(856, color="black", linestyle="--", linewidth=1.2, alpha=0.7)

    # Configure axes
    ax.set_xticks([143, 856])
    if show_xlabel:
        ax.set_xticklabels(["Midday", "Sunset"], fontsize=9)
        labels = ax.get_xticklabels()
        labels[1].set_fontweight("bold")
    else:
        ax.set_xticklabels([])

    if show_ylabel:
        ax.set_ylabel("Count of wet hour", fontsize=10)

    ax.set_ylim(y_lim)
    ax.set_yticks(y_ticks)

    if show_title:
        ax.set_title(intensity_label, fontsize=10, pad=10)

    if show_legend:
        ax.legend(bbox_to_anchor=(0.2, 0.02), loc="lower left", fontsize=9, frameon=False)


# ========== Composite Figure Helper ==========


def create_global_map_with_temporal_inset(
    ax1,
    temporal_stability,
    spatial_2020,
    COLORS,
    show_enhancement_text=False,
    legend_position="lower right",
    legend_fontsize=8,
    legend_markerscale=1.0,
):
    """
    Create Panel A: Global distribution map with temporal stability inset
    This function is used for creating the composite figure

    Parameters:
    -----------
    ax1 : matplotlib axis
        The axis to plot on
    temporal_stability : DataFrame
        20-year temporal stability data
    spatial_2020 : array
        2020 spatial data with columns [lat, lon, value]
    COLORS : dict
        Color scheme dictionary
    show_enhancement_text : bool, optional
        Whether to show the enhancement percentage annotation (default: False)
    legend_position : str or tuple, optional
        Legend position. Can be:
        - String: 'lower right', 'upper left', etc.
        - Tuple: (x, y) as fraction of axes (0-1), e.g., (0.7, 0.2) for 70% right, 20% up
    legend_fontsize : int, optional
        Font size for legend text (default: 8)
    legend_markerscale : float, optional
        Scale factor for legend markers (default: 1.0)

    Returns:
    --------
    enhancement_pct : float
        Percentage of cities showing enhancement
    """
    # Create the main map
    enhancement_pct = create_global_map_only(
        ax1,
        spatial_2020,
        COLORS,
        show_enhancement_text,
        legend_position,
        legend_fontsize,
        legend_markerscale,
    )

    # Add the temporal stability inset
    inset_ax, inset_ax2 = create_temporal_stability_inset(ax1, temporal_stability)

    return enhancement_pct
