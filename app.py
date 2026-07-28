"""Multi-year Streamlit dashboard for CSA STRATOS uPRISM open data.

Run from the project root with:
    streamlit run app.py
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from folium import CircleMarker, FeatureGroup, Map, Marker, PolyLine, TileLayer
from streamlit_folium import st_folium

from src.stratos_tracker.config import (
    AVAILABLE_YEARS,
    DATASET_LABELS,
    DEFAULT_YEAR,
    dataset_available,
    get_year_config,
)
from src.stratos_tracker.data import (
    camera_label,
    downsample_df,
    fetch_image,
    flight_events_df,
    load_environment,
    load_image_index,
    load_imu,
    load_track,
    load_trajectory,
    nearest_images_by_camera,
    nearest_row_by_time,
)

st.set_page_config(
    page_title="CSA Stratos Balloon Tracker",
    page_icon="🎈",
    layout="wide",
)

NO_VALUES = "No values found."


@st.cache_data(show_spinner="Downloading and preparing trajectory data...")
def cached_trajectory(year: int, source_key: str) -> pd.DataFrame:
    return load_trajectory(year, source_key)


@st.cache_data(show_spinner="Downloading and preparing IMU data...")
def cached_imu(year: int) -> pd.DataFrame:
    return load_imu(year)


@st.cache_data(show_spinner="Downloading external environmental data...")
def cached_environment(year: int) -> pd.DataFrame:
    return load_environment(year)


@st.cache_data(show_spinner="Downloading and preparing track-angle data...")
def cached_track(year: int) -> pd.DataFrame:
    return load_track(year)


@st.cache_data(show_spinner="Indexing onboard images...")
def cached_image_index(year: int) -> pd.DataFrame:
    return load_image_index(year)


@st.cache_data(show_spinner=False)
def cached_image(url: str):
    return fetch_image(url)


def format_number(value, suffix: str = "", digits: int = 2) -> str:
    """Format one scalar while keeping missing fields non-fatal."""
    if value is None or pd.isna(value):
        return "No values found"
    return f"{float(value):,.{digits}f}{suffix}"


def format_timestamp(timestamp: pd.Timestamp | None) -> str:
    if timestamp is None or pd.isna(timestamp):
        return "No values found"
    return pd.Timestamp(timestamp).strftime("%d %b %Y %H:%M:%S UTC")


def frame_has_values(df: pd.DataFrame | None, column: str) -> bool:
    """Return whether a frame contains at least one non-null value."""
    return (
        df is not None
        and not df.empty
        and column in df.columns
        and df[column].notna().any()
    )


def load_optional_frame(
    loader: Callable[[int], pd.DataFrame],
    year: int,
) -> tuple[pd.DataFrame, str | None]:
    """Load a non-essential section without preventing the app from rendering."""
    try:
        return loader(year), None
    except Exception as exc:  # Streamlit should show the other sections anyway.
        return pd.DataFrame(), str(exc)


def create_tracker_map(
    traj_df: pd.DataFrame,
    selected_time: pd.Timestamp,
    selected_row: pd.Series,
    map_style: str,
    max_points: int = 6000,
) -> Map:
    """Create a Folium map with full path, travelled path, and current marker."""
    display_df = downsample_df(traj_df, max_points=max_points)
    past_df = display_df[display_df["timestamp"] <= selected_time]

    current_location = [
        float(selected_row["latitude"]),
        float(selected_row["longitude"]),
    ]
    map_object = Map(
        location=current_location,
        zoom_start=7,
        tiles=None,
        control_scale=True,
    )

    if map_style == "Satellite":
        TileLayer(
            tiles=(
                "https://server.arcgisonline.com/ArcGIS/rest/services/"
                "World_Imagery/MapServer/tile/{z}/{y}/{x}"
            ),
            attr=(
                "Tiles © Esri — Sources: Esri, Maxar, Earthstar Geographics, "
                "and the GIS User Community"
            ),
            name="Satellite",
            control=False,
        ).add_to(map_object)
    elif map_style == "Light":
        TileLayer("CartoDB positron", name="Light", control=False).add_to(map_object)
    else:
        TileLayer("OpenStreetMap", name="OpenStreetMap", control=False).add_to(
            map_object
        )

    full_coords = display_df[["latitude", "longitude"]].dropna().values.tolist()
    past_coords = past_df[["latitude", "longitude"]].dropna().values.tolist()

    path_layer = FeatureGroup(name="Trajectory")
    if full_coords:
        PolyLine(
            full_coords,
            weight=3,
            opacity=0.35,
            tooltip="Full trajectory",
        ).add_to(path_layer)

    if past_coords:
        PolyLine(
            past_coords,
            weight=5,
            opacity=0.9,
            tooltip="Travelled trajectory",
        ).add_to(path_layer)

    path_layer.add_to(map_object)

    if full_coords:
        Marker(full_coords[0], tooltip="Start").add_to(map_object)
        Marker(full_coords[-1], tooltip="End").add_to(map_object)

    CircleMarker(
        location=current_location,
        radius=7,
        fill=True,
        fill_opacity=1,
        tooltip=f"Current position: {format_timestamp(selected_time)}",
    ).add_to(map_object)

    return map_object


def available_metric_frames(
    traj_df: pd.DataFrame,
    imu_df: pd.DataFrame,
    environment_df: pd.DataFrame,
    track_df: pd.DataFrame,
) -> dict[str, tuple[pd.DataFrame, str, str]]:
    """Return only metrics that exist for the selected year."""
    options: dict[str, tuple[pd.DataFrame, str, str]] = {}

    trajectory_metrics = {
        "Altitude": ("altitude_m", "Altitude [m]"),
        "Speed": ("speed_mps", "Speed [m/s]"),
        "Distance from origin": ("distance_from_origin_m", "Distance [m]"),
        "Distance travelled": ("distance_travelled_m", "Distance [m]"),
        "Heading": ("heading_deg", "Heading [degrees]"),
    }
    for label, (column, axis_title) in trajectory_metrics.items():
        if frame_has_values(traj_df, column):
            options[label] = (traj_df, column, axis_title)

    imu_metrics = {
        "IMU mean temperature": ("mean_temp_c", "Temperature [°C]"),
        "IMU ambient pressure": ("pressure_mbar", "Pressure [mbar]"),
        "IMU roll": ("cf_roll_rad", "Roll [radians]"),
        "IMU pitch": ("cf_pitch_rad", "Pitch [radians]"),
        "IMU yaw": ("cf_yaw_rad", "Yaw [radians]"),
    }
    for label, (column, axis_title) in imu_metrics.items():
        if frame_has_values(imu_df, column):
            options[label] = (imu_df, column, axis_title)

    environment_metrics = {
        "External temperature": ("external_temp_c", "Temperature [°C]"),
        "External pressure": ("external_pressure_hpa", "Pressure [hPa]"),
        "External humidity": ("external_humidity_pct", "Relative humidity [%]"),
        "uPRISM CPU temperature": ("cpu_temp_c", "Temperature [°C]"),
    }
    for label, (column, axis_title) in environment_metrics.items():
        if frame_has_values(environment_df, column):
            options[label] = (environment_df, column, axis_title)

    if frame_has_values(track_df, "track_angle_deg"):
        options["Track angle"] = (
            track_df,
            "track_angle_deg",
            "Degrees clockwise from north",
        )

    return options


def make_metric_chart(
    metric_df: pd.DataFrame,
    value_col: str,
    title: str,
    y_title: str,
    selected_time: pd.Timestamp,
    max_points: int = 8000,
) -> go.Figure:
    """Build a time-series chart with the selected flight time marked."""
    plot_df = metric_df[["timestamp", value_col]].dropna().copy()
    plot_df = downsample_df(plot_df, max_points=max_points)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df[value_col],
            mode="lines",
            name=title,
        )
    )
    figure.add_vline(
        x=selected_time,
        line_width=2,
        line_dash="dash",
    )
    figure.update_layout(
        title=title,
        xaxis_title="Time [UTC]",
        yaxis_title=y_title,
        height=320,
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    return figure


def display_optional_metric(
    label: str,
    row: pd.Series | None,
    column: str,
    suffix: str,
    digits: int = 2,
) -> bool:
    """Display a metric and return whether a value was available."""
    if row is None or column not in row.index or pd.isna(row.get(column)):
        return False
    st.write(f"**{label}**  {format_number(row.get(column), suffix, digits)}")
    return True


# ----------------------------- Sidebar controls -----------------------------
st.sidebar.text("🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈🎈")
st.sidebar.title("CSA Stratos Balloon Tracker")
st.sidebar.caption(
    "Select a year first. The remaining controls and datasets adapt "
    "to that year."
)

default_year_index = AVAILABLE_YEARS.index(DEFAULT_YEAR)
selected_year = st.sidebar.selectbox(
    "Selected year",
    options=AVAILABLE_YEARS,
    index=default_year_index,
    format_func=lambda year: get_year_config(year)["label"],
)
year_config = get_year_config(selected_year)
trajectory_sources = year_config["trajectory_sources"]

source_key = st.sidebar.selectbox(
    "Trajectory source",
    options=list(trajectory_sources),
    format_func=lambda key: f"{key} — {trajectory_sources[key]}",
    index=0,
)

if source_key == "ef_500hz":
    st.sidebar.warning(
        "The 500 Hz EF file is very large and is available only for the 2023 "
        "active-pointing windows. Loading it can take substantially longer."
    )

map_style = st.sidebar.selectbox(
    "Map style",
    ["Satellite", "OpenStreetMap", "Light"],
    index=0,
)

images_available = dataset_available(selected_year, "images")
if images_available:
    show_images = st.sidebar.checkbox(
        "Show nearest onboard images",
        value=False,
        help="Images are off by default to keep the tracker responsive.",
    )
else:
    show_images = False
    st.sidebar.caption("Onboard images: No values found for this year.")

with st.sidebar.expander(f"Dataset availability for {selected_year}"):
    availability_rows = []
    for key, label in DATASET_LABELS.items():
        availability_rows.append(
            {
                "Dataset": label,
                "Available": "Yes" if dataset_available(selected_year, key) else "No",
            }
        )
    st.dataframe(
        pd.DataFrame(availability_rows),
        use_container_width=True,
        hide_index=True,
    )


# ----------------------------- Data loading -----------------------------
try:
    traj_df = cached_trajectory(selected_year, source_key)
except Exception as exc:
    st.error(
        f"The selected {selected_year} trajectory file could not be loaded. "
        "Choose another trajectory source or verify the CSA data-server connection."
    )
    st.exception(exc)
    st.stop()

if traj_df.empty:
    st.error(
        "The selected trajectory file loaded, but no valid timestamp, latitude, "
        "and longitude rows were found."
    )
    st.stop()

imu_df, imu_error = load_optional_frame(cached_imu, selected_year)
environment_df, environment_error = load_optional_frame(
    cached_environment,
    selected_year,
)
track_df, track_error = load_optional_frame(cached_track, selected_year)


# ----------------------------- Timeline control -----------------------------
st.title(f"CSA STRATOS {selected_year} uPRISM Flight Tracker")
st.caption(year_config["campaign_summary"])

max_index = len(traj_df) - 1
timeline_key = f"flight_timeline_{selected_year}_{source_key}"
selected_idx = st.slider(
    "Flight timeline",
    min_value=0,
    max_value=max_index,
    value=0,
    step=1,
    key=timeline_key,
    help=(
        "Move the slider to update the map, chart, telemetry, environmental "
        "values, and available images for the selected year."
    ),
)

selected_row = traj_df.iloc[selected_idx]
selected_time = selected_row["timestamp"]
start_time = traj_df["timestamp"].iloc[0]
end_time = traj_df["timestamp"].iloc[-1]

st.markdown(
    f"**Selected time:** {format_timestamp(selected_time)}  "
    f"&nbsp;&nbsp;|&nbsp;&nbsp; "
    f"**Flight range:** {format_timestamp(start_time)} → "
    f"{format_timestamp(end_time)}",
    unsafe_allow_html=True,
)


# ----------------------------- Sidebar metrics -----------------------------
with st.sidebar.expander("Position & travel", expanded=True):
    st.write(
        f"**Longitude, latitude, altitude**  "
        f"{format_number(selected_row.get('longitude'), '°', 5)}, "
        f"{format_number(selected_row.get('latitude'), '°', 5)}, "
        f"{format_number(selected_row.get('altitude_m'), ' m', 2)}"
    )
    st.write(
        f"**Distance from origin**  "
        f"{format_number(selected_row.get('distance_from_origin_m'), ' m', 2)}"
    )
    st.write(
        f"**Distance travelled**  "
        f"{format_number(selected_row.get('distance_travelled_m'), ' m', 2)}"
    )
    if "speed_mps" in selected_row.index:
        st.write(
            f"**Speed**  {format_number(selected_row.get('speed_mps'), ' m/s', 2)}"
        )

imu_row = nearest_row_by_time(imu_df, selected_time)
environment_row = nearest_row_by_time(environment_df, selected_time)
track_row = nearest_row_by_time(track_df, selected_time)

with st.sidebar.expander("IMU sensor metrics", expanded=True):
    found_imu = False
    found_imu |= display_optional_metric(
        "Mean temperature",
        imu_row,
        "mean_temp_c",
        " °C",
    )

    if (
        imu_row is not None
        and "min_temp_c" in imu_row.index
        and "max_temp_c" in imu_row.index
        and not pd.isna(imu_row.get("min_temp_c"))
        and not pd.isna(imu_row.get("max_temp_c"))
    ):
        st.write(
            f"**Min / max temperature**  "
            f"{format_number(imu_row.get('min_temp_c'), ' °C', 2)} / "
            f"{format_number(imu_row.get('max_temp_c'), ' °C', 2)}"
        )
        found_imu = True

    found_imu |= display_optional_metric(
        "Ambient pressure",
        imu_row,
        "pressure_mbar",
        " mbar",
    )

    if not found_imu:
        st.write(NO_VALUES)

with st.sidebar.expander("External environmental metrics", expanded=True):
    found_environment = False
    found_environment |= display_optional_metric(
        "External temperature",
        environment_row,
        "external_temp_c",
        " °C",
    )
    found_environment |= display_optional_metric(
        "External pressure",
        environment_row,
        "external_pressure_hpa",
        " hPa",
    )
    found_environment |= display_optional_metric(
        "External humidity",
        environment_row,
        "external_humidity_pct",
        " %",
    )
    found_environment |= display_optional_metric(
        "uPRISM CPU temperature",
        environment_row,
        "cpu_temp_c",
        " °C",
    )
    if not found_environment:
        st.write(NO_VALUES)

with st.sidebar.expander("Track angle", expanded=True):
    if not display_optional_metric(
        "Track angle",
        track_row,
        "track_angle_deg",
        "°",
    ):
        st.write(NO_VALUES)

if show_images:
    with st.sidebar.expander("Images", expanded=True):
        try:
            image_index = cached_image_index(selected_year)
            nearest_images = nearest_images_by_camera(image_index, selected_time)

            if nearest_images.empty:
                st.info(NO_VALUES)
            else:
                for _, image_row in nearest_images.iterrows():
                    label = camera_label(selected_year, image_row["camera_id"])
                    st.caption(f"{label}: {image_row['filename']}")
                    try:
                        st.image(
                            cached_image(image_row["url"]),
                            use_container_width=True,
                        )
                    except Exception as image_exc:
                        st.warning(
                            f"Could not load {image_row['filename']}: {image_exc}"
                        )
        except Exception as image_index_exc:
            st.info(f"Image index unavailable: {image_index_exc}")


# ----------------------------- Main dashboard -----------------------------
metric_options = available_metric_frames(
    traj_df,
    imu_df,
    environment_df,
    track_df,
)

if not metric_options:
    st.warning("No chartable metric values were found for the selected source.")
else:
    metric_name = st.selectbox(
        "Chart",
        options=list(metric_options),
        index=0,
    )
    metric_df, metric_col, y_title = metric_options[metric_name]
    st.plotly_chart(
        make_metric_chart(
            metric_df,
            metric_col,
            metric_name,
            y_title,
            selected_time,
        ),
        use_container_width=True,
    )

map_object = create_tracker_map(
    traj_df,
    selected_time,
    selected_row,
    map_style,
)
st_folium(
    map_object,
    use_container_width=True,
    height=610,
    returned_objects=[],
)

with st.expander("Flight chronology annotations"):
    events = flight_events_df(selected_year)
    if events.empty:
        st.info(NO_VALUES)
    else:
        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True,
        )

with st.expander("Dataset load status"):
    configured_files = year_config["csv_files"]
    status_rows = [
        {
            "Section": "Trajectory",
            "Configured": "Yes",
            "Loaded rows": len(traj_df),
            "Status": "Loaded",
        },
        {
            "Section": "IMU",
            "Configured": "Yes" if dataset_available(selected_year, "imu") else "No",
            "Loaded rows": len(imu_df),
            "Status": imu_error or ("Loaded" if not imu_df.empty else "No values found"),
        },
        {
            "Section": "External environment",
            "Configured": (
                "Yes" if dataset_available(selected_year, "environment") else "No"
            ),
            "Loaded rows": len(environment_df),
            "Status": (
                environment_error
                or ("Loaded" if not environment_df.empty else "No values found")
            ),
        },
        {
            "Section": "Track angle",
            "Configured": "Yes" if dataset_available(selected_year, "track") else "No",
            "Loaded rows": len(track_df),
            "Status": track_error or ("Loaded" if not track_df.empty else "No values found"),
        },
        {
            "Section": "Images",
            "Configured": "Yes" if images_available else "No",
            "Loaded rows": "On demand" if images_available else 0,
            "Status": "Available on demand" if images_available else "No values found",
        },
    ]
    st.dataframe(
        pd.DataFrame(status_rows),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("**Configured files**")
    file_rows = []
    for key, info in configured_files.items():
        file_rows.append(
            {
                "Key": key,
                "Filename": info["filename"],
                "Expected rate": (
                    f"{info['expected_hz']} Hz"
                    if info.get("expected_hz") is not None
                    else "Not specified"
                ),
                "Description": info["description"],
            }
        )
    st.dataframe(
        pd.DataFrame(file_rows),
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Loaded trajectory details"):
    trajectory_info = year_config["csv_files"][source_key]
    st.write(f"**Selected year:** {selected_year}")
    st.write(f"**Trajectory file:** {trajectory_info['filename']}")
    st.write(f"**Rows:** {len(traj_df):,}")
    st.write(f"**Available standardized columns:** {', '.join(traj_df.columns)}")
    st.dataframe(
        traj_df.head(20),
        use_container_width=True,
    )