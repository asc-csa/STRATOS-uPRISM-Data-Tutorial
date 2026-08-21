<p align="center">
  <a href="https://github.com/asc-csa/STRATOS-uPRISM-Data-Tutorial/stargazers"><img src="https://img.shields.io/github/stars/asc-csa/STRATOS-uPRISM-Data-Tutorial" alt="Étoiles du dépôt GitHub"></a>&nbsp;
  <a href="https://github.com/asc-csa/STRATOS-uPRISM-Data-Tutorial/watchers"><img src="https://img.shields.io/github/watchers/asc-csa/STRATOS-uPRISM-Data-Tutorial" alt="Observateurs du dépôt GitHub"></a>&nbsp;
  <a href="https://github.com/asc-csa/STRATOS-uPRISM-Data-Tutorial/commits/main"><img src="https://img.shields.io/github/last-commit/asc-csa/STRATOS-uPRISM-Data-Tutorial" alt="Dernier commit sur GitHub"></a>&nbsp;
  <a href="https://github.com/asc-csa/STRATOS-uPRISM-Data-Tutorial/graphs/contributors"><img src="https://img.shields.io/github/contributors/asc-csa/STRATOS-uPRISM-Data-Tutorial" alt="Contributeurs sur GitHub"></a>&nbsp;
  <a href="https://twitter.com/intent/follow?screen_name=csa_asc"><img src="https://img.shields.io/twitter/follow/csa_asc?style=social" alt="Suivre l’Agence spatiale canadienne sur X"></a>
</p>

<a id="language-selection"></a>

# STRATOS uPRISM Open Data Tutorial / Tutoriel sur les données ouvertes STRATOS uPRISM

[**English**](#english) | [**Français**](#francais)

---

<a id="english"></a>

## English

Python tutorials and an interactive Streamlit dashboard for exploring the Canadian Space Agency (CSA) **Strato-Science 2022, 2023, and 2025 uPRISM open datasets**.

The project is designed as an educational companion to the official dataset documentation. It shows how to download the public files directly from the CSA open-data server, inspect their structure, identify data-quality issues, build cleaned analysis tables, visualize balloon trajectories, and export reproducible diagnostics without modifying the raw observations.

### Contents

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
- [Adding another campaign year](#adding-another-campaign-year)
- [Official documentation and data source](#official-documentation-and-data-source)

### Project overview

The repository contains two complementary ways to work with the datasets:

1. **Year-specific Jupyter notebooks** provide a transparent, step-by-step data-science workflow. They load the original files, inspect raw tables, validate timestamps and coordinates, detect anomalies, visualize the data, and export cleaned results and diagnostic tables.
2. **A multi-year Streamlit dashboard** provides an interactive flight tracker with a campaign selector, trajectory-source selector, timeline control, map, telemetry charts, flight-event annotations, and campaign-specific optional data.

The notebooks are intentionally self-contained so readers can see and modify the complete analysis workflow. The Streamlit application reuses the shared modules in `src/stratos_tracker/` to avoid duplicating dashboard logic.

### Supported campaigns

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

#### Campaign summary

- **2022 :** core navigation, dual GNSS, IMU, track angle, and two onboard cameras. The tutorial includes additional handling for older CSV formatting and a discontinuous navigation segment.
- **2023 :** includes the only 500 Hz EF file, a separate environmental file, NMEA records, and a documented navigation-sensor reset. No onboard images are included.
- **2025 :** includes core navigation, expanded NMEA analysis, track angle, and nadir images. The flight crosses midnight, so rollover is handled explicitly.

### Project structure

```text
.
├── documents/
│   ├── CSA-STRATOS-MAN-0014 P1 Strato-Science 2022 - uPRISM Open Data Readme (EN).pdf
│   ├── CSA-STRATOS-MAN-0015 P1 Strato-Science 2023 - uPRISM Open Data Readme (EN).pdf
│   └── CSA-STRATOS-MAN-0016 P1 Strato-Science 2025 - uPRISM Open Data Readme (EN).pdf
├── notebooks/
│   ├── stratos_2022_uprism_tutorial.ipynb
│   ├── stratos_2023_uprism_tutorial.ipynb
│   └── stratos_2025_uprism_tutorial.ipynb
├── src/
│   └── stratos_tracker/
│       ├── __init__.py
│       ├── config.py
│       └── data.py
├── .gitignore
├── README.md
├── app.py
└── requirements.txt
```

#### Main files

| Path | Purpose |
|---|---|
| `app.py` | Multi-year Streamlit flight-tracker interface. |
| `src/stratos_tracker/config.py` | Campaign-specific URLs, filenames, header modes, sampling rates, available trajectory sources, camera labels, and flight-event annotations. |
| `src/stratos_tracker/data.py` | Shared download, CSV parsing, timestamp handling, schema standardization, trajectory, distance, environmental, track-angle, and image-index helpers. |
| `notebooks/stratos_2022_uprism_tutorial.ipynb` | Full 2022 data-loading, validation, anomaly-detection, visualization, and export tutorial. |
| `notebooks/stratos_2023_uprism_tutorial.ipynb` | Full 2023 tutorial, including environmental data, navigation-reset context, and optional NMEA and 500 Hz analysis. |
| `notebooks/stratos_2025_uprism_tutorial.ipynb` | Full 2025 tutorial, including NMEA validation, midnight rollover, flight events, and image indexing. |
| `documents/` | Official CSA open-data readme manuals for the three campaigns. |

### Installation

Python **3.11** is recommended.

#### 1. Open a terminal in the project root

The commands below must be run from the directory containing `app.py`, `requirements.txt`, `notebooks/`, and `src/`.

#### 2. Create and activate a Conda environment

```bash
conda create -n stratos_tutorial python=3.11 -y
conda activate stratos_tutorial
```

#### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The project uses libraries including pandas, NumPy, Matplotlib, Plotly, Requests, Pillow, Beautiful Soup, Folium, Streamlit, and `streamlit-folium`.

#### 4. Select the environment in VS Code or Jupyter

When opening a notebook, select the `stratos_tutorial` environment as the notebook kernel. In VS Code, use **Select Kernel** in the upper-right corner of the notebook editor.

### Run the notebooks

Open the notebook for the campaign you want to study:

```text
notebooks/stratos_2022_uprism_tutorial.ipynb
notebooks/stratos_2023_uprism_tutorial.ipynb
notebooks/stratos_2025_uprism_tutorial.ipynb
```

Run the cells from top to bottom. Each notebook downloads its source files directly from the CSA open-data server, so an internet connection is required.

#### Optional loading controls

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

### Run the Streamlit dashboard

From the project root, run:

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally:

```text
http://localhost:8501
```

#### Dashboard features

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

### Tutorial workflow

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

### Generated outputs

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

### Data-quality considerations

#### All campaigns

- The campaign files have different schemas, sampling rates, and optional datasets.
- Some GNSS records may contain `(0°, 0°)` placeholders during initialization or reset periods.
- Missing values and validity flags must be inspected before filtering.
- Large spatial or altitude changes are reported as candidates and should be reviewed with surrounding rows and campaign context.
- UTC is used throughout the project unless a source field explicitly states otherwise.
- Units follow the source documentation and are primarily SI.

#### 2022

- Some older CSV rows contain trailing delimiters, which can make header and data-row widths appear inconsistent.
- Some timestamps occur near the GPS epoch in 1980 and are separated from the derived 2022 campaign view.
- A short segment contains a large position and ellipsoid-height discontinuity before returning to the main flight path.

#### 2023

- Some records contain GPS-epoch timestamp anomalies.
- A navigation-sensor reset occurred at approximately **07:18 UTC**, so gaps and discontinuities around the reset are inspected explicitly.
- The 500 Hz EF data are limited to active-pointing windows and are much larger than the standard files.
- The separate environmental dataset is unique to this supported campaign.

#### 2025

- The flight crosses midnight from August 21 to August 22, so time-only, NMEA, image, and event timestamps require rollover handling.
- NMEA records are parsed from a headerless file and checked for checksum validity, fix quality, coordinate validity, and agreement with GNSS1.
- Camera `0` is treated as the nadir-facing onboard camera.

### Implementation notes

#### Shared standardized schemas

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

#### Timestamp parsing

The shared data layer supports:

- full UTC datetime strings;
- time-of-day strings combined with the configured flight date;
- spreadsheet-style fractions of a day;
- seconds since midnight;
- midnight rollover between consecutive records.

#### Map and chart performance

The source data are preserved at their original loaded resolution. The dashboard downsamples only the displayed map and chart data when necessary to remain responsive.

#### Distance calculations

Distance from origin and cumulative distance travelled are calculated from latitude and longitude with the haversine great-circle formula.

#### Images

Image files are not stored in this repository. For campaigns with images, the application indexes filenames from the public directory and downloads only the selected nearest images on demand.

### Troubleshooting

#### `ModuleNotFoundError: No module named 'src'`

Run Streamlit from the project root:

```bash
streamlit run app.py
```

Do not run `app.py` from inside `src/` or `notebooks/`.

#### The notebook uses the wrong Python environment

In VS Code, select the `stratos_tutorial` kernel. Verify it with:

```python
import sys
print(sys.executable)
```

#### A Plotly figure does not appear in the notebook

Trust the notebook and confirm that the selected kernel has Plotly and Jupyter support installed. In VS Code, use **Trust** when prompted and rerun the visualization cell.

#### The dashboard or notebook is slow

- leave 2023 `LOAD_500_HZ` disabled unless that file is required;
- leave optional EF files disabled during an initial 2025 notebook run;
- keep onboard images disabled in the dashboard until needed;
- wait for the first download to complete—Streamlit caches prepared data for later reruns.

#### A campaign-specific section has no data

This can be expected. Dataset availability differs by year. The dashboard intentionally shows **“No values found”** for unsupported or empty optional sections instead of stopping the entire application.

#### A download fails

Confirm that the machine can access the CSA public data server and that no corporate proxy, VPN, or firewall is blocking the request. Then rerun the cell or clear the Streamlit cache:

```bash
streamlit cache clear
```

#### Excel displays unexpected timestamp values

Excel may automatically reformat the UTC timestamp column. Use pandas or another text-aware CSV reader to inspect the original values without spreadsheet date conversion.

### Adding another campaign year

To extend the dashboard and tutorials to another campaign:

1. add the official campaign manual to `documents/`;
2. add a new entry to `YEAR_CONFIGS` in `src/stratos_tracker/config.py`;
3. define the campaign files, header modes, sampling rates, trajectory sources, optional datasets, camera labels, and flight events;
4. update `src/stratos_tracker/data.py` only when the new schema requires additional parsing or standardized fields;
5. create a separate year-specific notebook so campaign-specific quality issues remain explicit and auditable;
6. update the availability table in this README.

### Official documentation and data source

The official CSA manuals included in this repository are the authoritative references for field definitions, units, coordinate frames, sampling rates, and flight chronology:

- [Strato-Science 2022 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0014%20P1%20Strato-Science%202022%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)
- [Strato-Science 2023 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0015%20P1%20Strato-Science%202023%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)
- [Strato-Science 2025 — uPRISM Open Data Readme](documents/CSA-STRATOS-MAN-0016%20P1%20Strato-Science%202025%20-%20uPRISM%20Open%20Data%20Readme%20%28EN%29.pdf)

Public data are downloaded from the CSA STRATOS open-data directory:

<https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/>

This repository is an educational analysis layer and does not replace the official documentation. Consult the corresponding manual before interpreting a field scientifically or using the data in published work.

[Back to language selection](#language-selection)

---

<a id="francais"></a>

## Français

Des tutoriels Python et un tableau de bord interactif Streamlit pour explorer les ensembles de données ouvertes Agence spatiale canadienne (ASC) **Strato-Science 2022, 2023 et 2025 uPRISM**.

Le projet est conçu comme un complément éducatif à la documentation officielle de l’ensemble de données. Il montre comment télécharger les fichiers publics directement à partir du serveur de données ouvertes de l’ASC, inspecter leur structure, identifier les problèmes de qualité des données, construire des tableaux d’analyse nettoyés, visualiser les trajectoires des ballons et exporter des diagnostics reproductibles sans modifier les observations brutes.

### Table des matières

- [Aperçu du projet](#fr-apercu-du-projet)
- [Campagnes prises en charge](#fr-campagnes-prises-en-charge)
- [Structure du projet](#fr-structure-du-projet)
- [Installation](#fr-installation)
- [Exécuter les bloc-notes](#fr-executer-les-bloc-notes)
- [Exécuter le tableau de bord Streamlit](#fr-executer-le-tableau-de-bord-streamlit)
- [Déroulement du tutoriel](#fr-deroulement-du-tutoriel)
- [Fichiers de sortie générés](#fr-fichiers-de-sortie-generes)
- [Considérations relatives à la qualité des données](#fr-qualite-des-donnees)
- [Notes sur l’implémentation](#fr-notes-sur-limplementation)
- [Dépannage](#fr-depannage)
- [Ajouter une autre année de campagne](#fr-ajouter-une-annee-de-campagne)
- [Documentation officielle et source des données](#fr-documentation-officielle)

<a id="fr-apercu-du-projet"></a>

### Aperçu du projet

Le référentiel contient deux façons complémentaires de travailler avec les ensembles de données :

1. **Les blocs-notes Jupyter spécifiques à l’année** fournissent un flux de travail transparent et étape par étape de la science des données. Ils chargent les fichiers originaux, inspectent les tableaux bruts, valident les horodatages et les coordonnées, détectent les anomalies, visualisent les données et exportent les résultats nettoyés et les tableaux de diagnostic.
2. **Un tableau de bord Streamlit pluriannuel** fournit un suivi de vol interactif avec un sélecteur de campagne, un sélecteur de trajectoire-source, un contrôle de la chronologie, une carte, des graphiques de télémétrie, des annotations d’événements de vol et des données facultatives spécifiques à la campagne.

Les carnets sont intentionnellement autonomes afin que les lecteurs puissent voir et modifier le flux de travail complet de l’analyse. L’application Streamlit réutilise les modules partagés dans « src/stratos_tracker/ » pour éviter de dupliquer la logique du tableau de bord.

<a id="fr-campagnes-prises-en-charge"></a>

### Campagnes prises en charge

Les ensembles de données de la campagne publique sont liés, mais ne sont **pas identiques**. L’application et les didacticiels gèrent la disponibilité et l’analyse séparément pour chaque année.

| Jeu de données ou fonctionnalité | 2022 | 2023 | 2025 |
|---|:---:|:---:|:---:|
| Filtre d’estimation, 1 Hz | Oui | Oui | Oui |
| Filtre d’estimation, 25 Hz | Oui | Oui | Oui |
| Filtre d’estimation, 500 Hz | Non | Oui, pendant les fenêtres de pointage actives | Non |
| Récepteur GNSS 1 | Oui, 1 Hz | Oui, champs à 1–2 Hz | Oui, champs à 1–2 Hz |
| Récepteur GNSS 2 | Oui, 1 Hz | Oui, champs à 1–2 Hz | Oui, champs à 1–2 Hz |
| IMU, attitude, température et pression | Oui | Oui | Oui |
| Données NMEA | Non | Oui | Oui |
| Données environnementales externes distinctes | Non | Oui | Non |
| Angle de piste | Oui | Oui | Oui |
| Images embarquées | Horizon et nadir | Non | Nadir |

#### Résumé des campagnes

- **2022 :** navigation de base, double GNSS, IMU, angle de trajectoire et deux caméras embarquées. Le didacticiel comprend une gestion supplémentaire pour les anciens formats CSV et un segment de navigation discontinu.
- **2023 :** comprend le seul fichier EF 500 Hz, un fichier environnemental séparé, des enregistrements NMEA et une réinitialisation documentée du capteur de navigation. Aucune image embarquée n’est incluse.
- **2025 :** comprend la navigation de base, l’analyse NMEA étendue, l’angle de la piste et les images du nadir. Le vol franchit minuit, donc le renversement est traité explicitement.

<a id="fr-structure-du-projet"></a>

### Structure du projet

```text
.
├── documents/
│   ├── CSA-STRATOS-MAN-0014 P1 Strato-Science 2022 - uPRISM Open Data Readme (EN).pdf
│   ├── CSA-STRATOS-MAN-0015 P1 Strato-Science 2023 - uPRISM Open Data Readme (EN).pdf
│   └── CSA-STRATOS-MAN-0016 P1 Strato-Science 2025 - uPRISM Open Data Readme (EN).pdf
├── notebooks/
│   ├── stratos_2022_uprism_tutorial.ipynb
│   ├── stratos_2023_uprism_tutorial.ipynb
│   └── stratos_2025_uprism_tutorial.ipynb
├── src/
│   └── stratos_tracker/
│       ├── __init__.py
│       ├── config.py
│       └── data.py
├── .gitignore
├── README.md
├── app.py
└── requirements.txt
```

#### Fichiers principaux

| Chemin | Objectif |
|---|---|
| 'app.py' | Interface pluriannuelle de suivi des vols Streamlit. |
| 'src/stratos_tracker/config.py' | URL spécifiques à la campagne, noms de fichiers, modes d’en-tête, taux d’échantillonnage, sources de trajectoire disponibles, étiquettes de caméra et annotations d’événements de vol. |
| 'src/stratos_tracker/data.py' | Téléchargement partagé, analyse CSV, gestion de l’horodatage, normalisation des schémas, assistances de trajectoire, de distance, d’environnement, d’angle de suivi et d’index d’image. |
| 'notebooks/stratos_2022_uprism_tutorial.ipynb' | Tutoriel complet sur le chargement, la validation, la détection des anomalies, la visualisation et l’exportation des données 2022. |
| 'notebooks/stratos_2023_uprism_tutorial.ipynb' | Tutoriel complet 2023, y compris les données environnementales, le contexte de réinitialisation de la navigation et l’analyse NMEA et 500 Hz en option. |
| 'notebooks/stratos_2025_uprism_tutorial.ipynb' | Tutoriel complet 2025, y compris la validation NMEA, le rollover de minuit, les événements de vol et l’indexation des images. |
| 'documents/' | Guides readme des données ouvertes officielles de l’ASC pour les trois campagnes. |

<a id="fr-installation"></a>

### Installation

Python **3.11** est recommandé.

#### 1. Ouvrir un terminal à la racine du projet

Les commandes ci-dessous doivent être exécutées à partir du répertoire contenant « app.py », « requirements.txt », « notebooks/ » et « src/ ».

#### 2. Créer et activer un environnement Conda

```bash
conda create -n stratos_tutorial python=3.11 -y
conda activate stratos_tutorial
```

#### 3. Installer les dépendances

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Le projet utilise des modules telles que pandas, NumPy, Matplotlib, Plotly, Requests, Pillow, Beautiful Soup, Folium, Streamlit et 'streamlit-folium'.

#### 4. Sélectionnez l’environnement dans VS Code ou Jupyter

Lorsque vous ouvrez un bloc-notes, sélectionnez l’environnement « stratos_tutorial » comme coeur du bloc-notes. Dans VS Code, utilisez **Select Kernel** dans le coin supérieur droit de l’éditeur de bloc-notes.

<a id="fr-executer-les-bloc-notes"></a>

### Exécuter les bloc-notes

Ouvrez le bloc-notes de la campagne que vous souhaitez étudier :

```text
notebooks/stratos_2022_uprism_tutorial.ipynb
notebooks/stratos_2023_uprism_tutorial.ipynb
notebooks/stratos_2025_uprism_tutorial.ipynb
```

Exécutez les cellules de haut en bas. Chaque bloc-notes télécharge ses fichiers sources directement à partir du serveur de données ouvertes de l’ASC, de sorte qu’une connexion Internet est nécessaire.

#### Options de chargement facultatives

Certains fichiers sont désactivés par défaut afin de limiter l’utilisation de la mémoire et le temps d’exécution. Modifiez ces variables dans la cellule de configuration de la campagne avant d’exécuter les cellules de chargement des données.

| bloc-note | Variable         | Valeur par défaut | Effet                                                                                                                                 |
| -------- | ---------------- | :---------------: | ------------------------------------------------------------------------------------------------------------------------------------- |
| 2022     | `LOAD_ALL_FILES` |      `False`      | Charge tous les tableaux configurés pour 2022 plutôt que l’ensemble par défaut comprenant les données GNSS1, IMU et d’angle de suivi. |
| 2023     | `LOAD_500_HZ`    |      `False`      | Charge et analyse le très volumineux fichier EF à 500 Hz.                                                                             |
| 2023     | `LOAD_NMEA`      |      `False`      | Charge le fichier NMEA de 2023, qui ne contient pas d’en-tête.                                                                        |
| 2025     | `LOAD_EF_25HZ`   |      `False`      | Charge le fichier EF à 25 Hz, qui est plus volumineux.                                                                                |
| 2025     | `LOAD_EF_1HZ`    |      `False`      | Charge le fichier EF supplémentaire à 1 Hz.                                                                                           |
| 2025     | `LOAD_NMEA`      |       `True`      | Analyse et valide les enregistrements NMEA de 2025.                                                                                   |
| 2025     | `INDEX_IMAGES`   |       `True`      | Indexe le répertoire public des images prises à bord en 2025.                                                                         |

Le téléchargement des fichiers volumineux peut prendre plusieurs minutes et nécessiter une quantité importante de mémoire. Laissez les fichiers facultatifs à haute fréquence désactivés lors de la première exécution.

<a id="fr-executer-le-tableau-de-bord-streamlit"></a>

### Exécuter le tableau de bord Streamlit

À partir de la racine du projet, exécutez la commande suivante :

```bash
streamlit run app.py
```

#### Fonctionnalités du tableau de bord

- sélectionner la campagne de 2022, 2023 ou 2025;
- sélectionner une source de trajectoire GNSS ou de filtre d’estimation disponible;
- parcourir manuellement le vol à l’aide d’un curseur chronologique;
- afficher l’itinéraire complet, l’itinéraire parcouru, les points de départ et d’arrivée ainsi que la position actuelle sur une carte 2D;
- basculer entre les fonds de carte satellite, OpenStreetMap et clair;
- tracer les mesures disponibles d’altitude, de vitesse, de distance, de cap, d’IMU, d’environnement, d’attitude et d’angle de suivi;
- consulter les annotations des événements de vol propres à chaque campagne;
- afficher les images prises à bord les plus proches lorsqu’elles sont disponibles pour l’année sélectionnée;
- consulter les fichiers configurés, le nombre de lignes chargées et les colonnes normalisées des trajectoires;
- continuer d’afficher les autres sections lorsqu’un jeu de données facultatif n’est pas disponible ou ne peut pas être chargé.

Le tableau de bord affiche **« Aucune valeur trouvée »** pour les données propres à une campagne qui n’existent pas, comme les images prises à bord en 2023 ou le fichier distinct de données environnementales en 2022 et en 2025.

<a id="fr-deroulement-du-tutoriel"></a>

### Déroulement du tutoriel

Bien que l’analyse exacte varie selon la campagne, les bloc-notes suivent le même déroulement général.

1. **Configurer la campagne** — définir la date du vol, les chemins du serveur public, les noms de fichiers, les fichiers facultatifs et les seuils de détection des anomalies.
2. **Charger les fichiers sources** — télécharger les fichiers CSV ou les répertoires d’images sans modifier les observations originales.
3. **Examiner les structures brutes** — examiner les en-têtes, les dimensions, les noms de champs, les caractéristiques d’échantillonnage et les formats propres à chaque campagne.
4. **Valider les horodatages** — repérer les incohérences entre l’année des enregistrements et celle de la campagne, les horodatages proches de l’époque GPS, les réinitialisations, les interruptions, les doublons et le passage à minuit.
5. **Examiner les valeurs manquantes et les indicateurs de validité** — signaler les données manquantes avant de déterminer les champs qui conviennent à l’analyse.
6. **Valider les coordonnées** — retirer des trajectoires dérivées les valeurs de remplacement `(0°, 0°)` et les valeurs de latitude ou de longitude impossibles.
7. **Détecter les discontinuités d’altitude et de position** — signaler les variations locales soudaines, les blocs temporaires, les grands sauts et les segments de trajectoire au lieu de relier silencieusement des points sans lien entre eux.
8. **Visualiser les données** — créer des graphiques de séries chronologiques ainsi que des trajectoires 2D et 3D nettoyées.
9. **Examiner les données propres à chaque campagne** — analyser les données environnementales externes, les enregistrements NMEA, les événements de pointage ou les images prises à bord lorsqu’ils sont disponibles.
10. **Exporter les résultats** — enregistrer les trajectoires finales nettoyées et les tableaux d’anomalies afin de pouvoir les examiner et les réutiliser.

Les DataFrames sources demeurent inchangés à des fins de traçabilité. Le nettoyage est appliqué aux tableaux dérivés, et les anomalies potentielles sont conservées en vue d’un examen scientifique plutôt que d’être automatiquement considérées comme des erreurs de capteur confirmées.

<a id="fr-fichiers-de-sortie-generes"></a>

### Fichiers de sortie générés

Lorsque la section d’exportation est exécutée, chaque bloc-note crée un répertoire propre à l’année dans le répertoire de travail actuel :

```text
tutorial_outputs_2022/
tutorial_outputs_2023/
tutorial_outputs_2025/
```

Selon la campagne et les options activées, les fichiers CSV exportés comprennent :

- les trajectoires GNSS et EF finales nettoyées;
- les lignes comportant des anomalies d’horodatage et les résumés des blocs d’anomalies;
- les anomalies potentielles d’altitude;
- les sauts spatiaux potentiels;
- les résumés des segments de trajectoire;
- les tableaux IMU, environnementaux et d’angle de suivi nettoyés;
- les résultats de l’inspection ou de la validation des données NMEA;
- les tableaux des événements de vol propres à chaque campagne;
- les index d’images et les tableaux des images les plus proches des événements.

Le fichier CSV de la trajectoire finale de chaque année est généré à partir du même DataFrame nettoyé que celui utilisé pour les visualisations finales en 2D et en 3D.

<a id="fr-qualite-des-donnees"></a>

### Considérations relatives à la qualité des données

#### Toutes les campagnes

- Les fichiers des campagnes présentent des schémas, des fréquences d’échantillonnage et des jeux de données facultatifs différents.
- Certains enregistrements GNSS peuvent contenir les valeurs de remplacement `(0°, 0°)` pendant les périodes d’initialisation ou de réinitialisation.
- Les valeurs manquantes et les indicateurs de validité doivent être examinés avant d’appliquer des filtres.
- Les variations importantes de position ou d’altitude sont signalées comme des anomalies potentielles et doivent être examinées avec les lignes environnantes et le contexte de la campagne.
- Le temps UTC est utilisé dans l’ensemble du projet, sauf si un champ source indique explicitement le contraire.
- Les unités sont conformes à la documentation source et sont principalement des unités du Système international (SI).

#### 2022

- Certaines lignes des anciens fichiers CSV comportent des délimiteurs à la fin, ce qui peut donner l’impression que l’en-tête et les lignes de données n’ont pas la même largeur.
- Certains horodatages se situent près de l’époque GPS en 1980 et sont séparés de la vue dérivée de la campagne de 2022.
- Un court segment présente une importante discontinuité de position et de hauteur ellipsoïdale avant de revenir à la trajectoire de vol principale.

#### 2023

- Certains enregistrements comportent des anomalies d’horodatage liées à l’époque GPS.
- Une réinitialisation du capteur de navigation s’est produite vers **07 h 18 UTC**; les interruptions et les discontinuités entourant cette réinitialisation sont donc examinées explicitement.
- Les données EF à 500 Hz sont limitées aux périodes de pointage actif et sont beaucoup plus volumineuses que les fichiers courants.
- Le jeu de données environnementales distinct est propre à cette campagne parmi celles prises en charge.

#### 2025

- Le vol se poursuit après minuit, du 21 au 22 août. Les horodatages contenant uniquement l’heure ainsi que ceux des données NMEA, des images et des événements nécessitent donc une gestion du changement de date.
- Les enregistrements NMEA sont analysés à partir d’un fichier sans en-tête et font l’objet de vérifications portant sur la validité de la somme de contrôle, la qualité de la position, la validité des coordonnées et la concordance avec GNSS1.
- La caméra `0` est considérée comme la caméra embarquée orientée vers le nadir.

<a id="fr-notes-sur-limplementation"></a>

### Notes sur l’implémentation

#### Schémas normalisés communs

Les fonctions de chargement du tableau de bord convertissent les colonnes sources propres à chaque campagne en noms cohérents, notamment :

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

Les tableaux normalisés facultatifs utilisent notamment les champs suivants :

```text
mean_temp_c
pressure_mbar
external_temp_c
external_pressure_hpa
external_humidity_pct
track_angle_deg
```

Un champ est affiché uniquement s’il existe et contient des valeurs utilisables pour la campagne sélectionnée.

#### Analyse des horodatages

La couche de données commune prend en charge :

- les chaînes complètes de date et d’heure en UTC;
- les chaînes contenant l’heure, combinées à la date de vol configurée;
- les fractions de journée au format utilisé par les tableurs;
- le nombre de secondes écoulées depuis minuit;
- le changement de date à minuit entre des enregistrements consécutifs.

#### Performance des cartes et des graphiques

Les données sources sont conservées à la résolution à laquelle elles ont été chargées. Au besoin, le tableau de bord réduit uniquement la fréquence des données affichées sur les cartes et les graphiques afin de maintenir une bonne réactivité.

#### Calculs de distance

La distance par rapport au point d’origine et la distance cumulée parcourue sont calculées à partir de la latitude et de la longitude à l’aide de la formule de Haversine pour les distances orthodromiques.

#### Images

Les fichiers d’images ne sont pas stockés dans ce dépôt. Pour les campagnes qui comprennent des images, l’application indexe les noms de fichiers dans le répertoire public et télécharge sur demande uniquement les images sélectionnées les plus proches.

<a id="fr-depannage"></a>

### Dépannage

#### `ModuleNotFoundError: No module named 'src'`

Exécutez Streamlit à partir de la racine du projet :

```bash
streamlit run app.py
```

#### Le bloc-note utilise le mauvais environnement Python

Dans VS Code, sélectionnez le noyau `stratos_tutorial`. Vérifiez-le à l’aide du code suivant :

```python
import sys
print(sys.executable)
```

#### Une figure Plotly ne s’affiche pas dans le bloc-note

Marquez le bloc-note comme fiable et confirmez que Plotly et la prise en charge de Jupyter sont installés dans le noyau sélectionné. Dans VS Code, cliquez sur **Trust** lorsque le logiciel vous y invite, puis exécutez de nouveau la cellule de visualisation.

#### Le tableau de bord ou le bloc-note est lent

- laissez la variable `LOAD_500_HZ` de 2023 désactivée, sauf si ce fichier est nécessaire;
- laissez les fichiers EF facultatifs désactivés lors de la première exécution du bloc-note de 2025;
- laissez les images prises à bord désactivées dans le tableau de bord jusqu’à ce qu’elles soient nécessaires;
- attendez la fin du premier téléchargement — Streamlit met les données préparées en cache pour les exécutions ultérieures.

#### Une section propre à une campagne ne contient aucune donnée

Cette situation peut être normale. La disponibilité des jeux de données varie selon l’année. Le tableau de bord affiche volontairement **« Aucune valeur trouvée »** pour les sections facultatives non prises en charge ou vides, au lieu d’interrompre l’ensemble de l’application.

#### Un téléchargement échoue

Vérifiez que l’ordinateur peut accéder au serveur public de données de l’ASC et qu’aucun serveur mandataire, réseau privé virtuel (RPV) ou pare-feu d’entreprise ne bloque la requête. Exécutez ensuite de nouveau la cellule ou videz le cache de Streamlit :

```bash
streamlit cache clear
```

#### Excel affiche des valeurs d’horodatage inattendues

Excel peut reformater automatiquement la colonne d’horodatage UTC. Utilisez pandas ou un autre lecteur CSV qui traite les données comme du texte afin d’examiner les valeurs originales sans conversion automatique des dates par le tableur.

<a id="fr-ajouter-une-annee-de-campagne"></a>

### Ajouter une autre année de campagne

Pour ajouter une autre campagne au tableau de bord et aux tutoriels :

1. ajoutez le manuel officiel de la campagne au répertoire `documents/`;
2. ajoutez une nouvelle entrée à `YEAR_CONFIGS` dans `src/stratos_tracker/config.py`;
3. définissez les fichiers de la campagne, les modes d’en-tête, les fréquences d’échantillonnage, les sources de trajectoire, les jeux de données facultatifs, les étiquettes des caméras et les événements de vol;
4. mettez à jour `src/stratos_tracker/data.py` uniquement si le nouveau schéma nécessite des traitements supplémentaires ou de nouveaux champs normalisés;
5. créez un bloc-note distinct pour la nouvelle année afin que les problèmes de qualité propres à la campagne demeurent explicites et vérifiables;
6. mettez à jour le tableau de disponibilité dans ce fichier README.

<a id="fr-documentation-officielle"></a>

### Documentation officielle et source des données

Les manuels officiels de l’ASC constituent les références faisant autorité pour les définitions des champs, les unités, les systèmes de coordonnées, les fréquences d’échantillonnage et la chronologie des vols :

- [Strato-Science 2022 — Lisez-moi des données ouvertes de l’uPRISM](https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/CSA-STRATOS-MAN-0014%20P1%20Strato-Science%202022%20-%20%20Lisez-moi%20des%20donn%c3%a9es%20ouvertes%20de%20l_uPRISM%20(FR).pdf)
- [Strato-Science 2023 — Lisez-moi des données ouvertes de l’uPRISM](https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/CSA-STRATOS-MAN-0015%20P1%20Strato-Science%202023%20-%20Lisez-moi%20des%20donn%c3%a9es%20ouvertes%20de%20l_uPRISM%20(FR).pdf)
- [Strato-Science 2025 — Lisez-moi des données ouvertes de l’uPRISM](https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/CSA-STRATOS-MAN-0016%20P1%20Strato-Science%202025%20-%20Lisez-moi%20des%20donn%c3%a9es%20ouvertes%20de%20l_uPRISM%20(FR).pdf)

Les données publiques sont téléchargées à partir du répertoire de données ouvertes STRATOS de l’ASC :

<https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/STRATOS/STRATOS/>

Ce dépôt constitue une couche d’analyse à des fins éducatives et ne remplace pas la documentation officielle. Consultez le manuel correspondant avant d’interpréter scientifiquement un champ ou d’utiliser les données dans des travaux publiés.

[Retour au choix de la langue](#language-selection)
