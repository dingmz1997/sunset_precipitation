"""
Data loader for temporal pattern analysis
Loads all precipitation intensity data into organized dictionaries
"""

import numpy as np
import pandas as pd


def load_temporal_data(data_dir="../data"):
    """
    Load all temporal pattern data for different precipitation intensities

    Returns:
    --------
    dict : Nested dictionary with structure:
        {
            'intensity_name': {
                'urban': {'mean': array, 'low': array, 'high': array},
                'rural': {'mean': array, 'low': array, 'high': array},
                'turban': {'mean': array, 'low': array, 'high': array}
            }
        }
    """

    # Define intensity categories
    intensities = {
        'low': '02_05',        # 0.2-0.5 mm/hr (low intensity)
        'moderate': '05_1',    # 0.5-1 mm/hr (moderate intensity)
        'other': '1'           # >1 mm/hr (other/heavy intensity)
    }

    data = {}

    # Load data for each intensity
    for name, suffix in intensities.items():
        data[name] = {
            'urban': {
                'mean': np.load(f"{data_dir}/urban_{suffix}_mean.npy"),
                'low': np.load(f"{data_dir}/urban_{suffix}_low.npy"),
                'high': np.load(f"{data_dir}/urban_{suffix}_high.npy")
            },
            'rural': {
                'mean': np.load(f"{data_dir}/rural_{suffix}_mean.npy"),
                'low': np.load(f"{data_dir}/rural_{suffix}_low.npy"),
                'high': np.load(f"{data_dir}/rural_{suffix}_high.npy")
            },
            'turban': {  # Urban-only events
                'mean': np.load(f"{data_dir}/turban_{suffix}_mean.npy"),
                'low': np.load(f"{data_dir}/turban_{suffix}_low.npy"),
                'high': np.load(f"{data_dir}/turban_{suffix}_high.npy")
            }
        }


    return data


def get_intensity_label(intensity_key):
    """
    Get human-readable label for intensity category

    Parameters:
    -----------
    intensity_key : str
        Key for intensity category ('low', 'moderate', 'other', 'low_moderate', 'all')

    Returns:
    --------
    str : Human-readable label
    """
    labels = {
        'low': '0.2-0.5 mm/hr',
        'moderate': '0.5-1 mm/hr',
        'other': '>1 mm/hr',
        'low_moderate': '0.2-1 mm/hr',
        'all': 'All intensities'
    }
    return labels.get(intensity_key, intensity_key)


def get_y_axis_limits(intensity_key, data_type='urban_rural'):
    """
    Get appropriate y-axis limits for different intensity categories and data types

    Parameters:
    -----------
    intensity_key : str
        Key for intensity category
    data_type : str
        'urban_rural' for urban vs rural comparison, 'turban' for urban-only events

    Returns:
    --------
    tuple : (y_min, y_max) for axis limits
    list : y_tick positions
    """

    if data_type == 'urban_rural':
        limits = {
            'low': ((6.8, 9.8), [7, 8, 9]),
            'moderate': ((5, 8), [5, 6, 7, 8]),
            'other': ((8, 16), [8, 10, 12, 14, 16]),
            'low_moderate': ((12, 18), [12, 14, 16, 18]),
            'all': ((20, 35), [20, 25, 30, 35])
        }
    else:  # turban
        limits = {
            'low': ((2.8, 4.2), [3.0, 3.5, 4.0]),
            'moderate': ((0.9, 1.3), [0.9, 1.0, 1.1, 1.2, 1.3]),
            'other': ((0.3, 0.7), [0.3, 0.4, 0.5, 0.6, 0.7]),
            'low_moderate': ((3.5, 5.5), [3.5, 4.0, 4.5, 5.0, 5.5]),
            'all': ((4, 7), [4, 5, 6, 7])
        }

    return limits.get(intensity_key, ((0, 10), [0, 2, 4, 6, 8, 10]))


def load_spatial_data(data_dir="../data", year=2020):
    """
    Load spatial data for a specific year or all years
    
    Parameters:
    -----------
    data_dir : str
        Path to data directory
    year : int or str
        Specific year (e.g., 2020) or 'all' for all available years
        
    Returns:
    --------
    np.array or dict : Spatial data for the specified year(s)
    """
    if year == 'all':
        # Load all available years (2001-2020)
        spatial_data = {}
        for yr in range(2001, 2021):
            try:
                spatial_data[yr] = np.loadtxt(f"{data_dir}/spa_{yr}.txt")
            except FileNotFoundError:
                print(f"Warning: spa_{yr}.txt not found")
                continue
        return spatial_data
    else:
        # Load specific year
        return np.loadtxt(f"{data_dir}/spa_{year}.txt")


# Temporal stability data (2001-2020)
temporal_stability = pd.DataFrame(
    {
        "year": list(range(2001, 2021)),
        "n_cities": [
            491,
            506,
            494,
            510,
            524,
            533,
            527,
            486,
            523,
            542,
            500,
            530,
            494,
            491,
            504,
            500,
            509,
            487,
            515,
            514,
        ],
        "enhancement_pct": [
            64.8,
            63.0,
            61.3,
            62.0,
            61.4,
            59.8,
            64.1,
            61.7,
            60.8,
            60.3,
            59.8,
            60.0,
            63.0,
            58.4,
            59.9,
            64.6,
            63.9,
            67.3,
            59.0,
            63.8,
        ],
    }
)

# Note: spatial_2020 should be loaded in the notebook with the correct path
# spatial_2020 = load_spatial_data("../data", 2020)

# Color scheme (colorblind-friendly)
COLORS = {
    "urban": "#D32F2F",  # Red for urban
    "rural": "#B8860B",  # Dark goldenrod for rural
    "urban_only": "#2E8B57",  # Sea green for urban-only
    "enhance_strong": (255 / 255, 120 / 255, 130 / 255),  # Strong suppression (red)
    "enhance_weak": (255 / 255, 179 / 255, 186 / 255),  # Weak suppression (pink)
    "suppress_weak": (180 / 255, 210 / 255, 100 / 255),  # Weak enhancement (light green)
    "suppress_strong": (120 / 255, 200 / 255, 150 / 255),  # Strong enhancement (green)
}
