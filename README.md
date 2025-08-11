# Sunset Precipitation Analysis

This repository contains data and analysis for the sunset precipitation study.

## Structure

```
├── data/               # Raw and processed data files
│   ├── *.npy          # NumPy arrays with precipitation intensity data
│   │   ├── rural_*    # Rural area measurements
│   │   ├── urban_*    # Urban area measurements
│   │   └── turban_*   # Transition urban area measurements
│   └── spa_*.txt      # Solar position algorithm data (2001-2020)
│
└── analysis/          # Analysis notebooks and scripts
    └── sunset_precipitation_analysis.ipynb  # Main analysis notebook
```

## Data Description

### Precipitation Intensity Files (*.npy)
- Three intensity categories:
  - `*_02_05_*`: 0.2-0.5 mm/h intensity
  - `*_05_1_*`: 0.5-1.0 mm/h intensity
  - `*_1_*`: >1.0 mm/h intensity
- Three statistical measures:
  - `*_mean.npy`: Mean values
  - `*_high.npy`: High percentile values
  - `*_low.npy`: Low percentile values
- Three regions:
  - `rural_*`: Rural area data
  - `urban_*`: Urban area data
  - `turban_*`: Transition urban area data

### Solar Position Algorithm Data (spa_*.txt)
Annual solar position data from 2001 to 2020 used for sunset time calculations.

## Usage

The analysis notebook processes the data files to investigate the relationship between sunset timing and precipitation patterns in urban vs rural areas.