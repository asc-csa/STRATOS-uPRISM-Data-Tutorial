# STRATOS uPRISM Open Data Tutorial

Python tutorials and an interactive Streamlit dashboard for exploring the Canadian Space Agency (CSA) **Strato-Science 2022, 2023, and 2025 uPRISM open datasets**.

The project is designed as an educational companion to the official dataset documentation. It shows how to download the public files directly from the CSA open-data server, inspect their structure, identify data-quality issues, build cleaned analysis tables, visualize balloon trajectories, and export reproducible diagnostics without modifying the raw observations.

## Contents

- [Project overview](#project-overview)
- [Supported campaigns](#supported-campaigns)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Run the notebooks](#run-the-notebooks)
- [Run the Streamlit dashboard](#run-the-streamlit-dashboard)
- [Tutorial workflow](#tutorial-workflow)
- [Generated outputs](#generated-outputs)
- [Data-quality considerations](#data-quality-considerations)
- [Implementation notes](#implementation-notes)
- [Troubleshooting](#troubleshooting)
- [Official documentation and data source](#official-documentation-and-data-source)

## Project overview

The repository contains two complementary ways to work with the datasets:

1. **Year-specific Jupyter notebooks** provide a transparent, step-by-step data-science workflow. They load the original files, inspect raw tables, validate timestamps and coordinates, detect anomalies, visualize the data, and export cleaned results and diagnostic tables.
2. **A multi-year Streamlit dashboard** provides an interactive flight tracker with a campaign selector, trajectory-source selector, timeline control, map, telemetry charts, flight-event annotations, and campaign-specific optional data.

The notebooks are intentionally self-contained so readers can see and modify the complete analysis workflow. The Streamlit application reuses the shared modules in `src/stratos_tracker/` to avoid duplicating dashboard logic.

## Supported campaigns

The public campaign datasets are related but are **not identical**. The application and tutorials handle availability and parsing separately for each year.

| Dataset or feature | 2022 | 2023 | 2025 |
|---|:---:|:---:|:---:|
| Estimation Filter, 1 Hz | Yes | Yes | Yes |
| Estimation Filter, 25 Hz | Yes | Yes | Yes |
| Estimation Filter, 500 Hz | No | Yes, during active pointing windows | No |
| GNSS receiver 1 | Yes, 1 Hz | Yes, fields at 1–2 Hz | Yes, fields at 1–2 Hz |
| GNSS receiver 2 | Yes, 1 Hz | Yes, fields at 1–2 Hz | Yes, fields at 1–2 Hz |
| IMU, attitude, temperature, and pressure | Yes | Yes | Yes |
| NMEA data | No | Yes | Yes |
| Separate external environmental data | No | Yes | No |
| Track angle | Yes | Yes | Yes |
| Onboard images | Horizon and nadir | No | Nadir |

### Campaign summary

- **2022 — baseline campaign:** core navigation, dual GNSS, IMU, track angle, and two onboard cameras. The tutorial includes additional handling for older CSV formatting and a discontinuous navigation segment.
- **2023 — most complete scientific dataset:** includes the only 500 Hz EF file, a separate environmental file, NMEA records, and a documented navigation-sensor reset. No onboard images are included.
- **2025 — streamlined campaign:** includes core navigation, expanded NMEA analysis, track angle, and nadir images. The flight crosses midnight, so rollover is handled explicitly.

## Project structure

```text
.
├── documents/
│   ├── CSA-STRATOS-MAN-0014 P1 Strato-Science 2022 - uPRISM Open Data Readme (EN).pdf
│   ├── CSA-STRATOS-MAN-0015 P1 Strato-Science 2023 - uPRISM Open Data Readme (EN).pdf
│   └── CSA-STRATOS-MAN-0016 P1 Strato-Science 2025 - uPRISM Open Data Readme (EN).pdf
├── notebooks/
│   ├── stratos_2022_uprism_tutorial.ipynb
│   ├── stratos_2023_uprism_tutorial.ipynb
│   └── stratos_2025_uprism_tutorial.ipynb
├── src/
│   └── stratos_tracker/
│       ├── __init__.py
│       ├── config.py
│       └── data.py
├── .gitignore
├── README.md
├── app.py
└── requirements.txt
```

### Main files

| Path | Purpose |
|---|---|
| `app.py` | Multi-year Streamlit flight-tracker interface. |
| `src/stratos_tracker/config.py` | Campaign-specific URLs, filenames, header modes, sampling rates, available trajectory sources, camera labels, and flight-event annotations. |
| `src/stratos_tracker/data.py` | Shared download, CSV parsing, timestamp handling, schema standardization, trajectory, distance, environmental, track-angle, and image-index helpers. |
| `notebooks/stratos_2022_uprism_tutorial.ipynb` | Full 2022 data-loading, validation, anomaly-detection, visualization, and export tutorial. |
| `notebooks/stratos_2023_uprism_tutorial.ipynb` | Full 2023 tutorial, including environmental data, navigation-reset context, and optional NMEA and 500 Hz analysis. |
| `notebooks/stratos_2025_uprism_tutorial.ipynb` | Full 2025 tutorial, including NMEA validation, midnight rollover, flight events, and image indexing. |
| `documents/` | Official CSA open-data readme manuals for the three campaigns. |

## Installation

Python **3.11** is recommended.

### 1. Open a terminal in the project root

The commands below must be run from the directory containing `app.py`, `requirements.txt`, `notebooks/`, and `src/`.

### 2. Create and activate a Conda environment

```bash
conda create -n stratos_tutorial python=3.11 -y
conda activate stratos_tutorial
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The project uses libraries including pandas, NumPy, Matplotlib, Plotly, Requests, Pillow, Beautiful Soup, Folium, Streamlit, and `streamlit-folium`.

### 4. Select the environment in VS Code or Jupyter

When opening a notebook, select the `stratos_tutorial` environment as the notebook kernel. In VS Code, use **Select Kernel** in the upper-right corner of the notebook editor.

## Run the notebooks

Open the notebook for the campaign you want to study:

```text
notebooks/stratos_2022_uprism_tutorial.ipynb
notebooks/stratos_2023_uprism_tutorial.ipynb
notebooks/stratos_2025_uprism_tutorial.ipynb
```

Run the cells from top to bottom. Each notebook downloads its source files directly from the CSA open-data server, so an internet connection is required.

### Optional loading controls

Some files are disabled by default to keep memory use and execution time manageable. Change these variables in the campaign-configuration cell before running the data-loading cells.

| Notebook | Variable | Default | Effect |
|---|---|:---:|---|
| 2022 | `LOAD_ALL_FILES` | `False` | Loads all configured 2022 tables instead of the default GNSS1, IMU, and track-angle set. |
| 2023 | `LOAD_500_HZ` | `False` | Loads and analyzes the very large 500 Hz EF file. |
| 2023 | `LOAD_NMEA` | `False` | Loads the 2023 headerless NMEA file. |
| 2025 | `LOAD_EF_25HZ` | `False` | Loads the larger 25 Hz EF file. |
| 2025 | `LOAD_EF_1HZ` | `False` | Loads the supplementary 1 Hz EF file. |
| 2025 | `LOAD_NMEA` | `True` | Parses and validates the 2025 NMEA records. |
| 2025 | `INDEX_IMAGES` | `True` | Indexes the public 2025 onboard-image directory. |

Large files can take several minutes to download and may require substantial memory. Leave the optional high-rate files disabled during an initial run.

## Run the Streamlit dashboard

From the project root, run:

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally:

```text
http://localhost:8501
```

### Dashboard features

- select the 2022, 2023, or 2025 campaign;
- select an available GNSS or estimation-filter trajectory source;
- move manually through the flight with a timeline slider;
- view the complete route, travelled route, start, end, and current position on a 2D map;
- switch between satellite, OpenStreetMap, and light map tiles;
- plot available altitude, speed, distance, heading, IMU, environmental, attitude, and track-angle measurements;
- inspect campaign-specific flight-event annotations;
- display the nearest onboard images when images exist for the selected year;
- inspect configured files, loaded row counts, and standardized trajectory columns;
- continue rendering other sections when an optional dataset is unavailable or fails to load.

The dashboard displays **“No values found”** for campaign-specific data that do not exist, such as onboard images in 2023 or the separate environmental file in 2022 and 2025.

## Tutorial workflow

Although the exact analysis varies by campaign, the notebooks follow the same general workflow.

1. **Configure the campaign** — define the flight date, public server paths, filenames, optional files, and anomaly thresholds.
2. **Load the source files** — download CSV or image-directory data without editing the original observations.
3. **Inspect raw structures** — examine headers, shapes, field names, sampling characteristics, and campaign-specific formats.
4. **Validate timestamps** — identify campaign-year mismatches, GPS-epoch records, resets, gaps, duplicates, and midnight rollover.
5. **Inspect missing values and validity flags** — report missingness before deciding which fields are suitable for analysis.
6. **Validate coordinates** — remove `(0°, 0°)` placeholders and impossible latitude or longitude values from derived trajectories.
7. **Detect altitude and spatial discontinuities** — report abrupt local changes, temporary blocks, large jumps, and trajectory segments rather than silently joining unrelated points.
8. **Visualize the data** — create time-series plots and cleaned 2D and 3D trajectories.
9. **Inspect campaign-specific data** — analyze external environment data, NMEA records, pointing events, or onboard images where available.
10. **Export results** — save final cleaned trajectories and anomaly tables for review and reuse.

The source dataframes remain unchanged for traceability. Cleaning is applied to derived tables, and anomaly candidates are retained for scientific review rather than being treated automatically as confirmed sensor errors.

## Generated outputs

When the export section is run, each notebook creates a year-specific directory in the current working directory:

```text
tutorial_outputs_2022/
tutorial_outputs_2023/
tutorial_outputs_2025/
```

Depending on the campaign and enabled options, the exported CSV files include:

- final cleaned GNSS and EF trajectories;
- timestamp-anomaly rows and anomaly-block summaries;
- altitude-anomaly candidates;
- spatial-jump candidates;
- trajectory-segment summaries;
- cleaned IMU, environmental, and track-angle tables;
- NMEA inspection or validation outputs;
- campaign flight-event tables;
- image indexes and nearest-event image tables.

The final trajectory CSV for each year is generated from the same cleaned dataframe used for the final 2D and 3D visualizations.

## Data-quality considerations

### All campaigns

- The campaign files have different schemas, sampling rates, and optional datasets.
- Some GNSS records may contain `(0°, 0°)` placeholders during initialization or reset periods.
- Missing values and validity flags must be inspected before filtering.
- Large spatial or altitude changes are reported as candidates and should be reviewed with surrounding rows and campaign context.
- UTC is used throughout the project unless a source field explicitly states otherwise.
- Units follow the source documentation and are primarily SI.

### 2022

- Some older CSV rows contain trailing delimiters, which can make header and data-row widths appear inconsistent.
- Some timestamps occur near the GPS epoch in 1980 and are separated from the derived 2022 campaign view.
- A short segment contains a large position and ellipsoid-height discontinuity before returning to the main flight path.

### 2023

- Some records contain GPS-epoch timestamp anomalies.
- A navigation-sensor reset occurred at approximately **07:18 UTC**, so gaps and discontinuities around the reset are inspected explicitly.
- The 500 Hz EF data are limited to active-pointing windows and are much larger than the standard files.
- The separate environmental dataset is unique to this supported campaign.

### 2025

- The flight crosses midnight from August 21 to August 22, so time-only, NMEA, image, and event timestamps require rollover handling.
- NMEA records are parsed from a headerless file and checked for checksum validity, fix quality, coordinate validity, and agreement with GNSS1.
- Camera `0` is treated as the nadir-facing onboard camera.

## Implementation notes

### Shared standardized schemas

The dashboard loaders convert campaign-specific source columns into consistent names such as:

```text
timestamp
latitude
longitude
altitude_m
speed_mps
heading_deg
distance_from_origin_m
distance_travelled_m
```

Optional standardized tables use fields such as:

```text
mean_temp_c
pressure_mbar
external_temp_c
external_pressure_hpa
external_humidity_pct
track_angle_deg
```

A field is displayed only when it exists and contains usable values for the selected campaign.

### Timestamp parsing

The shared data layer supports:

- full UTC datetime strings;
- time-of-day strings combined with the configured flight date;
- spreadsheet-style fractions of a day;
- seconds since midnight;
- midnight rollover between consecutive records.

### Map and chart performance

The source data are preserved at their original loaded resolution. The dashboard downsamples only the displayed map and chart data when necessary to remain responsive.

### Distance calculations

Distance from origin and cumulative distance travelled are calculated from latitude and longitude with the haversine great-circle formula.

### Images

Image files are not stored in this repository. For campaigns with images, the application indexes filenames from the public directory and downloads only the selected nearest images on demand.

## Troubleshooting

### `ModuleNotFoundError: No module named 'src'`

Run Streamlit from the project root:

```bash
streamlit run app.py
```

Do not run `app.py` from inside `src/` or `notebooks/`.

### The notebook uses the wrong Python environment

In VS Code, select the `stratos_tutorial` kernel. Verify it with:

```python
import sys
print(sys.executable)
```

### A Plotly figure does not appear in the notebook

Trust the notebook and confirm that the selected kernel has Plotly and Jupyter support installed. In VS Code, use **Trust** when prompted and rerun the visualization cell.

### The dashboard or notebook is slow

- leave 2023 `LOAD_500_HZ` disabled unless that file is required;
- leave optional EF files disabled during an initial 2025 notebook run;
- keep onboard images disabled in the dashboard until needed;
- wait for the first download to complete—Streamlit caches prepared data for later reruns.

### A campaign-specific section has no data

This can be expected. Dataset availability differs by year. The dashboard intentionally shows **“No values found”** for unsupported or empty optional sections instead of stopping the entire application.

### A download fails

Confirm that the machine can access the CSA public data server and that no corporate proxy, VPN, or firewall is blocking the request. Then rerun the cell or clear the Streamlit cache:

```bash
streamlit cache clear
```

### Excel displays unexpected timestamp values

Excel may automatically reformat the UTC timestamp column. Use pandas or another text-aware CSV reader to inspect the original values without spreadsheet date conversion.

## Adding another campaign year

To extend the dashboard and tutorials to another campaign:

1. add the official campaign manual to `documents/`;
2. add a new entry to `YEAR_CONFIGS` in `src/stratos_tracker/config.py`;
3. define the campaign files, header modes, sampling rates, trajectory sources, optional datasets, camera labels, and flight events;
4. update `src/stratos_tracker/data.py` only when the new schema requires additional parsing or standardized fields;
5. create a separate year-specific notebook so campaign-specific quality issues remain explicit and auditable;
6. update the availability table in this README.

## Official documentation and data source

The official CSA manuals included in this repository are the authoritative references for field definitions, units, coordinate frames, sampling rates, and flight chronology:

- [Strato-Science 2022 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0014%20P1%20Strato-Science%202022%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)
- [Strato-Science 2023 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0015%20P1%20Strato-Science%202023%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)
- [Strato-Science 2025 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0016%20P1%20Strato-Science%202025%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)

Public data are downloaded from the CSA STRATOS open-data directory:

<https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/>

This repository is an educational analysis layer and does not replace the official documentation. Consult the corresponding manual before interpreting a field scientifically or using the data in published work.
