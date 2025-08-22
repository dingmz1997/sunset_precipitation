# Sunset Precipitation Analysis

Analysis and visualization of urban sunset precipitation enhancement patterns across global cities (2001-2020).

## Key Finding
61.9% of cities globally show sunset precipitation enhancement, with remarkable temporal stability (58.4%-67.3%) across 20 years.

## Setup

This project uses `uv` for Python package management:

```bash
# Install dependencies
uv sync

# Run analysis notebook
uv run jupyter notebook analysis/composite_figure1_analysis.ipynb

# Or run standalone script
uv run python composite_figure1.py
```

## Project Structure

```
sunset_precipitation/
├── data/                  # Preprocessed temporal and spatial data
│   ├── urban_*.npy       # Urban precipitation patterns
│   ├── rural_*.npy       # Rural precipitation patterns
│   ├── turban_*.npy      # Urban-only precipitation events
│   └── spa_*.txt         # Spatial data by year (2001-2020)
├── analysis/             # Jupyter notebooks
│   ├── sunset_precipitation_analysis.ipynb    # Original analysis
│   └── composite_figure1_analysis.ipynb       # Enhanced Figure 1
├── figures/              # Output figures
├── composite_figure1.py  # Standalone figure generation script
└── pyproject.toml       # Project configuration
```

## Data Description

### Temporal Data (*.npy files)
- **Naming**: `{area}_{intensity}_{stat}.npy`
  - area: urban, rural, turban (urban-only)
  - intensity: 02_05 (0.2-0.5 mm/hr), 05_1 (0.5-1), 1 (>1)
  - stat: mean, low (95% CI lower), high (95% CI upper)
- **Structure**: 1000 interpolated points from midday to sunset

### Spatial Data (spa_*.txt)
- **Columns**: latitude, longitude, difference_index
- **DI Calculation**: (urban - rural) / rural × 100%
- **Years**: 2001-2020 (annual city extraction)

## Figure Generation

The composite Figure 1 includes:
- **Panel a**: Global distribution map with temporal stability inset
- **Panel b**: Urban vs rural temporal comparison (light precipitation)
- **Panel c**: Urban-only precipitation events (double peak pattern)

## Dependencies

- Python 3.13+
- numpy, pandas, matplotlib
- geopandas, contextily (for spatial visualization)
- jupyter, ipykernel (for notebooks)

## Development

```bash
# Install dev dependencies
uv add --dev black ruff ipdb

# Format code
uv run black .

# Lint code
uv run ruff check .
```