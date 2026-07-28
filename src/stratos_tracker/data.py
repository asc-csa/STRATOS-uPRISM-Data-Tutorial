"""Data loading and preprocessing helpers for the STRATOS tracker.

The public uPRISM campaign datasets are similar, but not identical. Every
loader therefore receives a campaign year and standardizes the available
columns into a stable schema used by the Streamlit application.
"""

from __future__ import annotations

import csv
import math
import re
from io import BytesIO, StringIO
from pathlib import Path
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import requests
import urllib3
from bs4 import BeautifulSoup
from PIL import Image

from .config import (
    DEFAULT_YEAR,
    dataset_available,
    get_csv_files,
    get_year_config,
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EARTH_RADIUS_M = 6_371_000


class DatasetUnavailableError(KeyError):
    """Raised when a file is not part of the selected campaign."""


def normalize_name(name: object) -> str:
    """Normalize a column name for loose matching."""
    return re.sub(r"[^a-z0-9]+", "", str(name).lower())


def make_unique(names: list[object]) -> list[str]:
    """Make duplicate column names unique by appending _1, _2, ..."""
    counts: dict[str, int] = {}
    out: list[str] = []
    for raw_name in names:
        name = str(raw_name).strip()
        if name not in counts:
            counts[name] = 0
            out.append(name)
        else:
            counts[name] += 1
            out.append(f"{name}_{counts[name]}")
    return out


def _clean_header_group(name: object) -> str:
    """Simplify a first-row uPRISM header group for duplicate subcolumns."""
    text = str(name).strip()
    if text.startswith("Unnamed") or text.lower() in {"", "nan"}:
        return ""

    # Remove hexadecimal descriptor text and device prefixes such as
    # "GNSS1:" or "IMU:" while preserving the physical group name.
    text = re.sub(r"\([^)]*0x[^)]*\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^[A-Za-z0-9_ -]+:\s*", "", text)
    return re.sub(r"\s+", " ", text).strip()


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Flatten one-row or two-row uPRISM headers into unique column names.

    The second header row normally contains useful names such as Latitude and
    Longitude. When a name like X, Y, or Z is repeated across several groups,
    the first-row group is included so the result remains meaningful, for
    example ``Scaled Accel X`` instead of ``X_2``.
    """
    if isinstance(df.columns, pd.MultiIndex):
        pairs = [(str(upper).strip(), str(lower).strip()) for upper, lower in df.columns]
        lower_norms = [
            normalize_name(lower)
            if not lower.startswith("Unnamed") and lower.lower() not in {"", "nan"}
            else ""
            for _, lower in pairs
        ]
        duplicate_lower = {
            name for name in lower_norms if name and lower_norms.count(name) > 1
        }
        group_aware_lower = {
            "x",
            "y",
            "z",
            "north",
            "east",
            "down",
            "roll",
            "pitch",
            "yaw",
            "q0",
            "q1",
            "q2",
            "q3",
        }

        new_cols: list[str] = []
        for (upper, lower), lower_norm in zip(pairs, lower_norms):
            upper_clean = _clean_header_group(upper)
            lower_is_missing = (
                lower.startswith("Unnamed") or lower == "" or lower.lower() == "nan"
            )

            if lower_is_missing:
                new_cols.append(upper_clean or upper)
            elif (
                lower_norm in duplicate_lower or lower_norm in group_aware_lower
            ) and upper_clean:
                new_cols.append(f"{upper_clean} {lower}".strip())
            else:
                new_cols.append(lower)

        out = df.copy()
        out.columns = make_unique(new_cols)
        return out

    out = df.copy()
    out.columns = make_unique([str(column).strip() for column in df.columns])
    return out


def fetch_text(url: str, timeout: int = 120) -> str:
    """Download a text file from the CSA open-data server."""
    response = requests.get(url, verify=False, timeout=timeout)
    response.raise_for_status()
    return response.text


def _header_quality_score(df: pd.DataFrame) -> int:
    """Score a parsed header so automatic one-row/two-row selection is stable."""
    normalized = [normalize_name(column) for column in df.columns]
    keywords = (
        "source",
        "utctimestamp",
        "timestamp",
        "packet",
        "latitude",
        "longitude",
        "trackangle",
        "cputemp",
        "externaltemp",
        "externalpress",
        "externalhumid",
    )
    return sum(any(keyword in column for column in normalized) for keyword in keywords)


def read_uprism_csv(
    url: str,
    header: str | None = "multi",
    names: list[str] | None = None,
    column_map: dict[int, str] | None = None,
    source_values: tuple[str, ...] | None = None,
) -> pd.DataFrame:
    """Read one uPRISM CSV file from a URL.

    The 2022 exports are read with ``header="positional"``. The manual defines
    their fields by column number, so this mode ignores inconsistent header
    formatting, keeps only actual data rows, and assigns documented names by
    zero-based position.
    """
    text = fetch_text(url)

    if header is None:
        return pd.read_csv(StringIO(text), header=None, names=names)

    if header == "positional":
        # Use the standard-library CSV reader so older files with header rows
        # of a different width cannot cause pandas to skip the wider data rows.
        rows = list(csv.reader(StringIO(text)))
        rows = [row for row in rows if any(str(value).strip() for value in row)]
        if not rows:
            return pd.DataFrame()

        width = max(len(row) for row in rows)
        raw = pd.DataFrame(
            [row + [""] * (width - len(row)) for row in rows],
            dtype=str,
        )

        # Header rows use labels such as "Packet Header" and "Source". Data
        # rows begin with LOGQ7 (GQ7 files) or PRISM (track-angle file).
        allowed_sources = {
            value.strip().upper()
            for value in (source_values or ("LOGQ7", "PRISM"))
        }
        first_column = (
            raw.iloc[:, 0]
            .astype(str)
            .str.replace("\ufeff", "", regex=False)
            .str.strip()
            .str.upper()
        )
        data_mask = first_column.isin(allowed_sources)
        parsed = raw.loc[data_mask].copy()

        if parsed.empty:
            # Do not silently return header rows. This message is much more
            # useful than a later "no valid latitude" error.
            observed = ", ".join(first_column.drop_duplicates().head(8).tolist())
            raise ValueError(
                "No data rows were detected in the positional uPRISM CSV. "
                f"Expected first-column values {sorted(allowed_sources)}; "
                f"observed examples: {observed or 'none'}."
            )

        columns = [f"column_{index}" for index in range(parsed.shape[1])]
        for index, name in (column_map or {}).items():
            if 0 <= int(index) < len(columns):
                columns[int(index)] = name
        parsed.columns = make_unique(columns)
        return parsed.reset_index(drop=True)

    if header == "multi":
        return flatten_columns(pd.read_csv(StringIO(text), header=[0, 1]))

    if header == "single":
        return flatten_columns(pd.read_csv(StringIO(text), header=0))

    if header == "auto":
        candidates: list[pd.DataFrame] = []
        for header_value in (0, [0, 1]):
            try:
                candidate = flatten_columns(
                    pd.read_csv(StringIO(text), header=header_value)
                )
                candidates.append(candidate)
            except (pd.errors.ParserError, ValueError):
                continue

        if not candidates:
            raise ValueError(f"Could not determine the CSV header format for {url}")

        return max(candidates, key=_header_quality_score)

    raise ValueError(f"Unknown header mode: {header}")


def _resolve_year_and_key(
    year_or_key: int | str,
    key: str | None,
) -> tuple[int, str]:
    """Support both new ``(year, key)`` and old 2025-only ``(key)`` calls."""
    if key is None:
        return DEFAULT_YEAR, str(year_or_key)
    return int(year_or_key), key


def load_csv_by_key(
    year_or_key: int | str,
    key: str | None = None,
) -> pd.DataFrame:
    """Load one configured CSV file.

    Preferred usage is ``load_csv_by_key(2023, "environment")``. For backward
    compatibility, ``load_csv_by_key("gnss1")`` still loads the 2025 file.
    """
    year, resolved_key = _resolve_year_and_key(year_or_key, key)
    files = get_csv_files(year)

    if resolved_key not in files:
        valid = ", ".join(files)
        raise DatasetUnavailableError(
            f"Dataset {resolved_key!r} is not available for {year}. "
            f"Available keys: {valid}"
        )

    info = files[resolved_key]
    base_url = get_year_config(year)["base_url_csv"]
    url = urljoin(base_url, info["filename"])

    if resolved_key == "nmea":
        return read_uprism_csv(url, header=None, names=["nmea_sentence"])
    return read_uprism_csv(
        url,
        header=info["header"],
        column_map=info.get("column_map"),
        source_values=info.get("source_values"),
    )


def find_column(
    df: pd.DataFrame,
    candidates: list[str],
    required: bool = False,
) -> str | None:
    """Find a column using exact normalized matching, then contains matching."""
    normalized_to_actual = {normalize_name(column): column for column in df.columns}

    for candidate in candidates:
        key = normalize_name(candidate)
        if key in normalized_to_actual:
            return normalized_to_actual[key]

    for candidate in candidates:
        key = normalize_name(candidate)
        for column in df.columns:
            if key and key in normalize_name(column):
                return column

    if required:
        raise KeyError(f"Could not find any of these columns: {candidates}")
    return None


def parse_utc(
    series: pd.Series,
    default_date: str | None = None,
) -> pd.Series:
    """Parse uPRISM timestamps and return timezone-aware UTC values.

    In addition to full datetimes, the 2022 files may expose time-of-day
    values. This parser supports clock strings, Excel-style fractions of a
    day, and seconds since midnight, while detecting midnight rollover.
    """
    raw = (
        series.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.replace(r"\s+UTC$", "", regex=True, case=False)
    )

    result = pd.Series(pd.NaT, index=series.index, dtype="datetime64[ns, UTC]")

    if not default_date:
        return pd.to_datetime(raw, utc=True, errors="coerce")

    base_date = pd.Timestamp(default_date, tz="UTC").normalize()

    # Full date/time values are parsed directly. Numeric and clock-only values
    # are handled below so pandas cannot interpret them relative to today.
    full_datetime_mask = raw.str.contains(r"[-/]", regex=True, na=False)
    if full_datetime_mask.any():
        result.loc[full_datetime_mask] = pd.to_datetime(
            raw.loc[full_datetime_mask],
            utc=True,
            errors="coerce",
        )

    clock_mask = raw.str.match(
        r"^\d{1,2}:\d{2}(?::\d{2}(?:[.,]\d+)?)?Z?$",
        na=False,
    )

    day_offset = 0
    previous_seconds: float | None = None

    def assign_elapsed(index: object, seconds: float) -> None:
        nonlocal day_offset, previous_seconds
        if previous_seconds is not None and seconds < previous_seconds - 6 * 3600:
            day_offset += 1
        result.loc[index] = (
            base_date
            + pd.Timedelta(days=day_offset)
            + pd.Timedelta(seconds=seconds)
        )
        previous_seconds = seconds

    for index in raw[clock_mask].index:
        value = raw.loc[index].rstrip("Z").replace(",", ".")
        parts = value.split(":")
        if len(parts) == 2:
            value = f"{parts[0]}:{parts[1]}:00"
        delta = pd.to_timedelta(value, errors="coerce")
        if not pd.isna(delta):
            assign_elapsed(index, float(delta.total_seconds()))

    # Some spreadsheet exports represent a clock time as a fraction of a day
    # (for example 0.5 = 12:00) or as seconds since midnight.
    remaining_mask = result.isna() & ~full_datetime_mask & ~clock_mask
    numeric = pd.to_numeric(raw.where(remaining_mask), errors="coerce")
    numeric_values = numeric.dropna()
    use_fractional_days = (
        not numeric_values.empty
        and numeric_values.between(0, 2, inclusive="left").mean() >= 0.9
    )

    for index in numeric_values.index:
        value = float(numeric.loc[index])
        seconds = value * 86400.0 if use_fractional_days else value
        if 0 <= seconds < 172800:
            assign_elapsed(index, seconds % 86400.0)

    # Last fallback for uncommon but valid timestamp strings.
    fallback_mask = result.isna()
    if fallback_mask.any():
        fallback = pd.to_datetime(raw.loc[fallback_mask], utc=True, errors="coerce")
        result.loc[fallback_mask] = fallback

    return result


def to_numeric_safe(series: pd.Series) -> pd.Series:
    """Convert a pandas series to numeric values, coercing invalid values."""
    return pd.to_numeric(series, errors="coerce")


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    """Return an empty frame with a predictable schema."""
    return pd.DataFrame({column: pd.Series(dtype="object") for column in columns})


def build_trajectory_df(
    df: pd.DataFrame,
    source_name: str = "dataset",
    flight_date: str | None = None,
) -> pd.DataFrame:
    """Standardize a GNSS or EF frame into a tracker-ready trajectory table."""
    time_col = find_column(
        df,
        ["UTC Timestamp", "UTC timestamp", "Timestamp", "Time"],
        required=True,
    )
    lat_col = find_column(df, ["Latitude", "Lat"], required=True)
    lon_col = find_column(df, ["Longitude", "Lon", "Long"], required=True)
    alt_col = find_column(
        df,
        [
            "Altitude",
            "Ellipsoid Height",
            "Height Above Ellipsoid",
            "MSL Height",
        ],
        required=False,
    )

    out = pd.DataFrame(
        {
            "timestamp": parse_utc(df[time_col], default_date=flight_date),
            "latitude": to_numeric_safe(df[lat_col]),
            "longitude": to_numeric_safe(df[lon_col]),
        }
    )

    if alt_col is not None:
        out["altitude_m"] = to_numeric_safe(df[alt_col])

    optional_groups = {
        "vel_n_mps": ["Velocity North", "North Velocity", "NED Velocity North", "North"],
        "vel_e_mps": ["Velocity East", "East Velocity", "NED Velocity East", "East"],
        "vel_d_mps": ["Velocity Down", "Down Velocity", "NED Velocity Down", "Down"],
        "speed_mps": ["Ground Speed", "Speed"],
        "roll_rad": ["Roll", "CF Roll"],
        "pitch_rad": ["Pitch", "CF Pitch"],
        "yaw_rad": ["Yaw", "CF Yaw"],
        "heading_deg": ["Heading"],
    }

    used_cols = {time_col, lat_col, lon_col, alt_col}
    for standard_name, candidates in optional_groups.items():
        column = find_column(df, candidates, required=False)
        if column is not None and column not in used_cols:
            out[standard_name] = to_numeric_safe(df[column])
            used_cols.add(column)

    if "speed_mps" not in out.columns:
        velocity_columns = ["vel_n_mps", "vel_e_mps", "vel_d_mps"]
        if all(column in out.columns for column in velocity_columns):
            out["speed_mps"] = np.sqrt(
                out["vel_n_mps"] ** 2
                + out["vel_e_mps"] ** 2
                + out["vel_d_mps"] ** 2
            )

    out["source"] = source_name
    out = out.dropna(subset=["timestamp", "latitude", "longitude"])
    out = out.sort_values("timestamp").reset_index(drop=True)
    return add_distance_columns(out)


def load_trajectory(
    year_or_source: int | str = DEFAULT_YEAR,
    source_key: str | None = None,
) -> pd.DataFrame:
    """Load and standardize one trajectory source.

    New usage: ``load_trajectory(2023, "gnss1")``.
    Old usage: ``load_trajectory("gnss1")`` loads 2025.
    """
    year, resolved_source = _resolve_year_and_key(year_or_source, source_key)
    files = get_csv_files(year)
    raw = load_csv_by_key(year, resolved_source)
    return build_trajectory_df(
        raw,
        source_name=files[resolved_source]["filename"],
        flight_date=get_year_config(year)["flight_date"],
    )


def build_imu_df(
    imu_df: pd.DataFrame,
    flight_date: str | None = None,
) -> pd.DataFrame:
    """Standardize useful IMU, attitude, temperature, and pressure fields."""
    time_col = find_column(
        imu_df,
        ["UTC Timestamp", "UTC timestamp", "Timestamp", "Time"],
        required=True,
    )

    out = pd.DataFrame(
        {"timestamp": parse_utc(imu_df[time_col], default_date=flight_date)}
    )

    candidates = {
        "min_temp_c": ["Min Temp", "Minimum Temp", "Min Temperature"],
        "max_temp_c": ["Max Temp", "Maximum Temp", "Max Temperature"],
        "mean_temp_c": ["Mean Temp", "Mean Temperature"],
        "pressure_mbar": ["Pressure", "Scaled Ambient Pressure"],
        "accel_x_g": ["Scaled Accel X", "Scaled Accelerometer X"],
        "accel_y_g": ["Scaled Accel Y", "Scaled Accelerometer Y"],
        "accel_z_g": ["Scaled Accel Z", "Scaled Accelerometer Z"],
        "gyro_x_rad_s": ["Scaled Gyro X"],
        "gyro_y_rad_s": ["Scaled Gyro Y"],
        "gyro_z_rad_s": ["Scaled Gyro Z"],
        "cf_roll_rad": ["CF Roll", "Complementary Filter Roll"],
        "cf_pitch_rad": ["CF Pitch", "Complementary Filter Pitch"],
        "cf_yaw_rad": ["CF Yaw", "Complementary Filter Yaw"],
    }

    for output_column, names in candidates.items():
        column = find_column(imu_df, names, required=False)
        if column is not None:
            out[output_column] = to_numeric_safe(imu_df[column])

    return out.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def load_imu(year: int = DEFAULT_YEAR) -> pd.DataFrame:
    """Load and standardize the campaign IMU file."""
    if not dataset_available(year, "imu"):
        return _empty_frame(
            ["timestamp", "min_temp_c", "max_temp_c", "mean_temp_c", "pressure_mbar"]
        )
    return build_imu_df(
        load_csv_by_key(year, "imu"),
        flight_date=get_year_config(year)["flight_date"],
    )


def build_environment_df(
    environment_df: pd.DataFrame,
    flight_date: str | None = None,
) -> pd.DataFrame:
    """Standardize the separate 2023 external environmental dataset."""
    time_col = find_column(
        environment_df,
        ["UTC Timestamp", "UTC timestamp", "Timestamp", "Time"],
        required=True,
    )
    out = pd.DataFrame(
        {"timestamp": parse_utc(environment_df[time_col], default_date=flight_date)}
    )

    candidates = {
        "cpu_temp_c": ["CPU Temp", "CPU Temperature"],
        "external_temp_c": ["External Temp", "External Temperature"],
        "external_pressure_hpa": [
            "External Press",
            "External Pressure",
        ],
        "external_humidity_pct": [
            "External Humid",
            "External Humidity",
            "External Relative Humidity",
        ],
    }

    for output_column, names in candidates.items():
        column = find_column(environment_df, names, required=False)
        if column is not None:
            out[output_column] = to_numeric_safe(environment_df[column])

    return out.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def load_environment(year: int = DEFAULT_YEAR) -> pd.DataFrame:
    """Load the separate external environment file when a campaign has one."""
    if not dataset_available(year, "environment"):
        return _empty_frame(
            [
                "timestamp",
                "cpu_temp_c",
                "external_temp_c",
                "external_pressure_hpa",
                "external_humidity_pct",
            ]
        )
    return build_environment_df(
        load_csv_by_key(year, "environment"),
        flight_date=get_year_config(year)["flight_date"],
    )


def build_track_df(
    track_df: pd.DataFrame,
    flight_date: str | None = None,
) -> pd.DataFrame:
    """Standardize a track-angle file."""
    time_col = find_column(
        track_df,
        ["UTC Timestamp", "UTC timestamp", "Timestamp", "Time"],
        required=True,
    )
    angle_col = find_column(track_df, ["Track Angle"], required=True)
    valid_col = find_column(track_df, ["Track Angle Valid"], required=False)

    out = pd.DataFrame(
        {
            "timestamp": parse_utc(track_df[time_col], default_date=flight_date),
            "track_angle_deg": to_numeric_safe(track_df[angle_col]),
        }
    )
    if valid_col is not None:
        out["track_angle_valid"] = to_numeric_safe(track_df[valid_col])

    return out.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def load_track(year: int = DEFAULT_YEAR) -> pd.DataFrame:
    """Load and standardize the campaign track-angle file."""
    if not dataset_available(year, "track"):
        return _empty_frame(["timestamp", "track_angle_deg", "track_angle_valid"])
    return build_track_df(
        load_csv_by_key(year, "track"),
        flight_date=get_year_config(year)["flight_date"],
    )


def flight_events_df(year: int = DEFAULT_YEAR) -> pd.DataFrame:
    """Return campaign-specific flight chronology annotations."""
    events = pd.DataFrame(
        get_year_config(year)["flight_events"],
        columns=["timestamp", "event"],
    )
    if events.empty:
        return events
    events["timestamp"] = pd.to_datetime(events["timestamp"], utc=True, errors="coerce")
    return events.dropna(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)


def haversine_distance_m(
    lat1: pd.Series | np.ndarray | float,
    lon1: pd.Series | np.ndarray | float,
    lat2: pd.Series | np.ndarray | float,
    lon2: pd.Series | np.ndarray | float,
) -> pd.Series | np.ndarray | float:
    """Great-circle distance between WGS84 latitude/longitude points."""
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(a))


def add_distance_columns(traj_df: pd.DataFrame) -> pd.DataFrame:
    """Add distance-from-origin and cumulative-distance columns."""
    df = traj_df.copy()
    if df.empty:
        df["distance_from_origin_m"] = pd.Series(dtype="float64")
        df["distance_travelled_m"] = pd.Series(dtype="float64")
        return df

    origin_lat = df["latitude"].iloc[0]
    origin_lon = df["longitude"].iloc[0]
    df["distance_from_origin_m"] = haversine_distance_m(
        origin_lat,
        origin_lon,
        df["latitude"],
        df["longitude"],
    )

    previous_latitude = df["latitude"].shift(1)
    previous_longitude = df["longitude"].shift(1)
    step_m = haversine_distance_m(
        previous_latitude,
        previous_longitude,
        df["latitude"],
        df["longitude"],
    )
    df["distance_travelled_m"] = pd.Series(step_m, index=df.index).fillna(0).cumsum()
    return df


def nearest_row_by_time(
    df: pd.DataFrame,
    timestamp: pd.Timestamp,
) -> pd.Series | None:
    """Return the row closest to a timestamp."""
    if df is None or df.empty or "timestamp" not in df.columns:
        return None

    usable = df.dropna(subset=["timestamp"])
    if usable.empty:
        return None

    target = pd.Timestamp(timestamp)
    if target.tzinfo is None:
        target = target.tz_localize("UTC")
    else:
        target = target.tz_convert("UTC")

    index = (usable["timestamp"] - target).abs().idxmin()
    return usable.loc[index]


def downsample_df(df: pd.DataFrame, max_points: int = 5000) -> pd.DataFrame:
    """Downsample evenly for display without changing the source data."""
    if len(df) <= max_points:
        return df.copy()
    step = int(math.ceil(len(df) / max_points))
    return df.iloc[::step].copy()


def fetch_directory_links(url: str) -> list[str]:
    """List file links from a simple web-directory page."""
    html = fetch_text(url)
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        if href:
            links.append(urljoin(url, href))
    return sorted(set(links))


def parse_image_filename(url: str) -> dict[str, object] | None:
    """Parse image filenames such as ``0_20250821_145300.jpg``."""
    filename = Path(url).name
    match = re.match(
        r"(?P<camera>\d+)_(?P<date>\d{8})_(?P<time>\d{6})\.jpe?g$",
        filename,
        re.IGNORECASE,
    )
    if not match:
        return None

    timestamp = pd.to_datetime(
        match.group("date") + match.group("time"),
        format="%Y%m%d%H%M%S",
        utc=True,
        errors="coerce",
    )
    if pd.isna(timestamp):
        return None

    return {
        "camera_id": match.group("camera"),
        "timestamp": timestamp,
        "filename": filename,
        "url": url,
    }


def load_image_index(
    year_or_url: int | str = DEFAULT_YEAR,
) -> pd.DataFrame:
    """Build an image index for a campaign.

    Passing a URL remains supported for older notebook cells. Passing a year is
    preferred because camera availability differs by campaign.
    """
    if isinstance(year_or_url, str) and year_or_url.lower().startswith(("http://", "https://")):
        base_url = year_or_url
    else:
        year = int(year_or_url)
        base_url = get_year_config(year).get("base_url_images")

    if not base_url:
        return _empty_frame(["camera_id", "timestamp", "filename", "url"])

    rows: list[dict[str, object]] = []
    for link in fetch_directory_links(base_url):
        if not link.lower().endswith((".jpg", ".jpeg")):
            continue
        parsed = parse_image_filename(link)
        if parsed is not None:
            rows.append(parsed)

    if not rows:
        return _empty_frame(["camera_id", "timestamp", "filename", "url"])

    return (
        pd.DataFrame(rows)
        .sort_values(["camera_id", "timestamp"])
        .reset_index(drop=True)
    )


def camera_label(
    year_or_camera: int | str,
    camera_id: object | None = None,
) -> str:
    """Return a campaign-specific human-readable camera label."""
    if camera_id is None:
        year = DEFAULT_YEAR
        resolved_camera_id = year_or_camera
    else:
        year = int(year_or_camera)
        resolved_camera_id = camera_id

    labels = get_year_config(year).get("camera_labels", {})
    return labels.get(
        str(resolved_camera_id),
        f"Camera {resolved_camera_id}",
    )


def nearest_images_by_camera(
    image_index: pd.DataFrame,
    timestamp: pd.Timestamp,
    max_time_difference_minutes: int = 10,
) -> pd.DataFrame:
    """Return the nearest image to a timestamp for each camera."""
    if image_index is None or image_index.empty:
        columns = list(image_index.columns) if image_index is not None else []
        return pd.DataFrame(columns=columns)

    target = pd.Timestamp(timestamp)
    if target.tzinfo is None:
        target = target.tz_localize("UTC")
    else:
        target = target.tz_convert("UTC")

    rows = []
    max_delta = pd.Timedelta(minutes=max_time_difference_minutes)
    for _, group in image_index.groupby("camera_id"):
        deltas = (group["timestamp"] - target).abs()
        index = deltas.idxmin()
        if deltas.loc[index] <= max_delta:
            row = group.loc[index].copy()
            row["time_difference_seconds"] = deltas.loc[index].total_seconds()
            rows.append(row)

    if not rows:
        return pd.DataFrame(
            columns=list(image_index.columns) + ["time_difference_seconds"]
        )
    return pd.DataFrame(rows).sort_values("camera_id").reset_index(drop=True)


def fetch_image(url: str, timeout: int = 60) -> Image.Image:
    """Download an image from a URL as an RGB PIL image."""
    response = requests.get(url, verify=False, timeout=timeout)
    response.raise_for_status()
    return Image.open(BytesIO(response.content)).convert("RGB")