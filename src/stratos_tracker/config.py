"""Configuration values for the multi-year STRATOS uPRISM tracker.

The datasets are configured per campaign because the available files, sampling
rates, image cameras, and flight chronology differ between 2022, 2023, and 2025.
"""

from __future__ import annotations

from typing import Any

DATA_SERVER_ROOT = (
    "https://donnees-data.asc-csa.gc.ca/users/OpenData_DonneesOuvertes/pub/"
    "STRATOS/STRATOS/"
)

DEFAULT_YEAR = 2025


def _csv_file(
    filename: str,
    description: str,
    *,
    header: str | None = "multi",
    expected_hz: float | None = None,
    column_map: dict[int, str] | None = None,
    source_values: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Create one CSV-file configuration entry.

    ``column_map`` is used for the 2022 exports. Those files are parsed by
    documented column position instead of relying on the two header rows. This
    is more reliable for the older export format while preserving the newer
    2023 and 2025 header-based readers.
    """
    return {
        "filename": filename,
        "description": description,
        "header": header,
        "expected_hz": expected_hz,
        "column_map": column_map,
        "source_values": source_values,
    }


YEAR_CONFIGS: dict[int, dict[str, Any]] = {
    2022: {
        "label": "2022",
        "campaign_summary": (
            "Baseline uPRISM dataset with core EF, dual-GNSS, IMU, track-angle, "
            "and onboard image data. It does not include NMEA, a separate "
            "environmental file, or 500 Hz EF data."
        ),
        "flight_date": "2022-08-22",
        "base_url_csv": DATA_SERVER_ROOT + "uprism_data_2022/",
        "base_url_images": DATA_SERVER_ROOT + "uprism_images_2022/",
        "csv_files": {
            # The 2022 manual defines the variables by zero-based column
            # position (Tables 5-1 through 5-5). The older files are therefore
            # parsed positionally instead of depending on header formatting.
            "ef_1hz": _csv_file(
                "GQ7_EF_1hz_20220822.csv",
                "Supplementary estimation-filter data sampled at 1 Hz",
                header="positional",
                expected_hz=1,
                source_values=("LOGQ7",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "Filter State",
                    4: "Dynamics Mode",
                    5: "Status Flags",
                },
            ),
            "ef_25hz": _csv_file(
                "GQ7_EF_25hz_20220822.csv",
                "Core estimation-filter navigation data sampled at 25 Hz",
                header="positional",
                expected_hz=25,
                source_values=("LOGQ7",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "GPS TOW",
                    4: "GPS Weeks",
                    5: "GPS Timestamp Valid",
                    6: "Latitude",
                    7: "Longitude",
                    8: "Altitude",
                    9: "LLH Valid",
                    10: "Velocity North",
                    11: "Velocity East",
                    12: "Velocity Down",
                    13: "Velocity Valid",
                    14: "Roll",
                    15: "Pitch",
                    16: "Yaw",
                    17: "Euler Valid",
                    18: "Comp Angular Rate X",
                    19: "Comp Angular Rate Y",
                    20: "Comp Angular Rate Z",
                    21: "Comp Angular Rate Valid",
                },
            ),
            "gnss1": _csv_file(
                "GQ7_GNSS1_20220822.csv",
                "GNSS receiver 1 data sampled at 1 Hz",
                header="positional",
                expected_hz=1,
                source_values=("LOGQ7",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "Latitude",
                    4: "Longitude",
                    5: "Ellipsoid Height",
                    6: "MSL Height",
                    7: "Horizontal Accuracy",
                    8: "Vertical Accuracy",
                    9: "Position Valid",
                    10: "Velocity North",
                    11: "Velocity East",
                    12: "Velocity Down",
                    13: "Speed",
                    14: "Ground Speed",
                    15: "Heading",
                    16: "Speed Accuracy",
                    17: "Heading Accuracy",
                    18: "NED VEL Valid",
                },
            ),
            "gnss2": _csv_file(
                "GQ7_GNSS2_20220822.csv",
                "GNSS receiver 2 data sampled at 1 Hz",
                header="positional",
                expected_hz=1,
                source_values=("LOGQ7",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "Latitude",
                    4: "Longitude",
                    5: "Ellipsoid Height",
                    6: "MSL Height",
                    7: "Horizontal Accuracy",
                    8: "Vertical Accuracy",
                    9: "Position Valid",
                    10: "Velocity North",
                    11: "Velocity East",
                    12: "Velocity Down",
                    13: "Speed",
                    14: "Ground Speed",
                    15: "Heading",
                    16: "Speed Accuracy",
                    17: "Heading Accuracy",
                    18: "NED VEL Valid",
                },
            ),
            "imu": _csv_file(
                "GQ7_IMU_20220822.csv",
                "IMU, attitude, temperature, and pressure data sampled at 1 Hz",
                header="positional",
                expected_hz=1,
                source_values=("LOGQ7",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "Scaled Accel X",
                    4: "Scaled Accel Y",
                    5: "Scaled Accel Z",
                    6: "Scaled Gyro X",
                    7: "Scaled Gyro Y",
                    8: "Scaled Gyro Z",
                    9: "Scaled Magnetometer X",
                    10: "Scaled Magnetometer Y",
                    11: "Scaled Magnetometer Z",
                    12: "CF q0",
                    13: "CF q1",
                    14: "CF q2",
                    15: "CF q3",
                    16: "CF Roll",
                    17: "CF Pitch",
                    18: "CF Yaw",
                    19: "GPS TOW",
                    20: "GPS Week Num",
                    21: "GPS Time Valid",
                    22: "Min Temp",
                    23: "Max Temp",
                    24: "Mean Temp",
                    25: "Pressure",
                },
            ),
            "track": _csv_file(
                "SWNAV_AHR0_track_angle_20220822.csv",
                "Track angle calculated at 1 Hz",
                header="positional",
                expected_hz=1,
                source_values=("PRISM",),
                column_map={
                    0: "Source",
                    1: "UTC Timestamp",
                    2: "Packet",
                    3: "Track Angle",
                    4: "Track Angle Valid",
                },
            ),
        },
        "trajectory_sources": {
            "gnss1": "GNSS receiver 1, 1 Hz",
            "gnss2": "GNSS receiver 2, 1 Hz",
            "ef_25hz": "Estimation filter, 25 Hz",
        },
        # Camera IDs are campaign-specific. In 2022, camera 0 faced the
        # horizon and camera 1 faced nadir.
        "camera_labels": {
            "0": "Horizon",
            "1": "Nadir",
        },
        "flight_events": [
            ("2022-08-22 01:56:00", "Beginning of data"),
            (
                "2022-08-22 14:23:06",
                "uPRISM powered off due to concerns of overheating",
            ),
            ("2022-08-22 15:04:12", "uPRISM powered on"),
            ("2022-08-22 15:10:02", "uPRISM powered off"),
        ],
    },
    2023: {
        "label": "2023",
        "campaign_summary": (
            "The most complete scientific dataset: core and supplementary EF, "
            "500 Hz EF windows, dual-GNSS, IMU, NMEA, a separate external "
            "environmental dataset, and track angle. No onboard image dataset "
            "is included."
        ),
        "flight_date": "2023-08-22",
        "base_url_csv": DATA_SERVER_ROOT + "uprism_data_2023/",
        "base_url_images": None,
        "csv_files": {
            "ef_1hz": _csv_file(
                "GQ7_EF_1hz_20230822.csv",
                "Supplementary estimation-filter data sampled at 1 Hz",
                expected_hz=1,
            ),
            "ef_25hz": _csv_file(
                "GQ7_EF_25hz_20230822.csv",
                "Core estimation-filter navigation data sampled at 25 Hz",
                expected_hz=25,
            ),
            "ef_500hz": _csv_file(
                "GQ7_EF_500hz_20230822.csv",
                (
                    "Core estimation-filter navigation data sampled at 500 Hz "
                    "during active pointing windows"
                ),
                expected_hz=500,
            ),
            "gnss1": _csv_file(
                "GQ7_GNSS1_20230822.csv",
                "GNSS receiver 1 data sampled at 1 Hz and 2 Hz by field",
                expected_hz=2,
            ),
            "gnss2": _csv_file(
                "GQ7_GNSS2_20230822.csv",
                "GNSS receiver 2 data sampled at 1 Hz and 2 Hz by field",
                expected_hz=2,
            ),
            "imu": _csv_file(
                "GQ7_IMU_20230822.csv",
                "IMU, attitude, temperature, and pressure data sampled at 1 Hz",
                expected_hz=1,
            ),
            "nmea": _csv_file(
                "GQ7_NMEA_20230822.csv",
                "GPGGA NMEA sentences output at 1 Hz; no CSV header",
                header=None,
                expected_hz=1,
            ),
            "environment": _csv_file(
                "PRISM_HW1_env_20230822.csv",
                "External temperature, pressure, humidity, and CPU temperature at 0.5 Hz",
                header="auto",
                expected_hz=0.5,
            ),
            "track": _csv_file(
                "SWNAV_AHR0_track_angle_20230822.csv",
                "Track angle calculated at 1 Hz",
                header="auto",
                expected_hz=1,
            ),
        },
        "trajectory_sources": {
            "gnss1": "GNSS receiver 1, 2 Hz",
            "gnss2": "GNSS receiver 2, 2 Hz",
            "ef_25hz": "Estimation filter, 25 Hz",
            "ef_500hz": "Estimation filter, 500 Hz — very large file",
        },
        "camera_labels": {},
        "flight_events": [
            ("2023-08-22 02:00", "Begin moving payload gondola to tarmac"),
            ("2023-08-22 03:00", "Navigation sensor heater ON at 100%"),
            ("2023-08-22 03:06", "Navigation sensor heater OFF"),
            ("2023-08-22 03:41", "Navigation sensor heater ON at 100%"),
            ("2023-08-22 04:54", "Nimbus-3 launch"),
            (
                "2023-08-22 07:03",
                "Pointing system ON in damping mode; GQ7 EF telemetry set to 500 Hz",
            ),
            ("2023-08-22 07:03", "Pointing system OFF"),
            ("2023-08-22 07:18", "Navigation sensor reset"),
            ("2023-08-22 07:36", "Reached flight ceiling"),
            (
                "2023-08-22 07:49",
                "Pointing system ON in damping mode; GQ7 EF telemetry set to 500 Hz",
            ),
            (
                "2023-08-22 07:53",
                "Pointing system set to ralliement mode, pointing to 56°",
            ),
            ("2023-08-22 07:57", "Pointing system set to performance mode"),
            (
                "2023-08-22 08:01",
                "Ralliement mode; inertial pointing to Vega",
            ),
            ("2023-08-22 08:06", "Pointing system set to performance mode"),
            (
                "2023-08-22 08:42",
                "Applied new gains for performance mode",
            ),
            (
                "2023-08-22 08:51",
                "Navigation sensor heater OFF; sensor showed 53 °C",
            ),
            ("2023-08-22 09:34", "Pointing system OFF"),
            ("2023-08-22 09:39", "uPRISM power OFF"),
            (
                "2023-08-22 09:55",
                "Separation / start of descent under parachute",
            ),
            ("2023-08-22 10:23", "Landing"),
        ],
    },
    2025: {
        "label": "2025",
        "campaign_summary": (
            "Streamlined, user-friendly dataset with core navigation, dual-GNSS, "
            "IMU, expanded NMEA, track angle, and onboard nadir images. It does "
            "not include a separate environmental file or 500 Hz EF data."
        ),
        "flight_date": "2025-08-21",
        "base_url_csv": DATA_SERVER_ROOT + "uprism_data_2025/",
        "base_url_images": DATA_SERVER_ROOT + "uprism_images_2025/",
        "csv_files": {
            "ef_1hz": _csv_file(
                "GQ7_EF_1hz_20250821.csv",
                "Supplementary estimation-filter data sampled at 1 Hz",
                expected_hz=1,
            ),
            "ef_25hz": _csv_file(
                "GQ7_EF_25hz_20250821.csv",
                "Core estimation-filter navigation data sampled at 25 Hz",
                expected_hz=25,
            ),
            "gnss1": _csv_file(
                "GQ7_GNSS1_20250821.csv",
                "GNSS receiver 1 data sampled at 1 Hz and 2 Hz by field",
                expected_hz=2,
            ),
            "gnss2": _csv_file(
                "GQ7_GNSS2_20250821.csv",
                "GNSS receiver 2 data sampled at 1 Hz and 2 Hz by field",
                expected_hz=2,
            ),
            "imu": _csv_file(
                "GQ7_IMU_20250821.csv",
                "IMU, attitude, temperature, and pressure data sampled at 1 Hz",
                expected_hz=1,
            ),
            "nmea": _csv_file(
                "GQ7_NMEA_20250821.csv",
                "GPGGA/GPRMC NMEA sentences output at 1 Hz; no CSV header",
                header=None,
                expected_hz=1,
            ),
            "track": _csv_file(
                "SWNAV_AHR0_track_angle_20250821.csv",
                "Track angle calculated at 1 Hz",
                header="auto",
                expected_hz=1,
            ),
        },
        "trajectory_sources": {
            "gnss1": "GNSS receiver 1, 2 Hz",
            "gnss2": "GNSS receiver 2, 2 Hz",
            "ef_25hz": "Estimation filter, 25 Hz",
        },
        "camera_labels": {
            "0": "Nadir",
        },
        "flight_events": [
            ("2025-08-21 14:53", "Nimbus-2 launch"),
            ("2025-08-21 16:46", "Start of pointing operations"),
            ("2025-08-21 17:05", "Sun pointing"),
            (
                "2025-08-21 18:41",
                "Four 360° rotations at 0.4°/s with pauses",
            ),
            ("2025-08-21 20:12", "Sun pointing"),
            (
                "2025-08-21 21:43",
                "Two 360° rotations at 2°/s with a pause",
            ),
            ("2025-08-21 22:18", "Sun pointing"),
            ("2025-08-21 22:43", "Anti-sun pointing with offset"),
            ("2025-08-21 23:20", "Pointing at 296°"),
            ("2025-08-21 23:28", "Pointing at 294.8°"),
            ("2025-08-22 00:47", "Pointing at 204.8°"),
            (
                "2025-08-22 00:56",
                "Pointing toward 24.8° at 0.214°/s",
            ),
            ("2025-08-22 01:13", "Pointing at 294.8°"),
            ("2025-08-22 02:50", "End of pointing operations"),
            (
                "2025-08-22 04:01",
                "Separation / start of descent under parachute",
            ),
        ],
    },
}

AVAILABLE_YEARS = tuple(sorted(YEAR_CONFIGS))

DATASET_LABELS = {
    "ef_1hz": "EF 1 Hz",
    "ef_25hz": "EF 25 Hz",
    "ef_500hz": "EF 500 Hz",
    "gnss1": "GNSS receiver 1",
    "gnss2": "GNSS receiver 2",
    "imu": "IMU",
    "nmea": "NMEA GNSS",
    "environment": "External environment",
    "track": "Track angle",
    "images": "Images",
}


def get_year_config(year: int) -> dict[str, Any]:
    """Return a campaign configuration and validate the selected year."""
    try:
        return YEAR_CONFIGS[int(year)]
    except (KeyError, TypeError, ValueError) as exc:
        valid = ", ".join(str(value) for value in AVAILABLE_YEARS)
        raise KeyError(f"Unknown campaign year {year!r}. Valid years: {valid}") from exc


def get_csv_files(year: int) -> dict[str, dict[str, Any]]:
    """Return the configured CSV files for one year."""
    return get_year_config(year)["csv_files"]


def get_trajectory_sources(year: int) -> dict[str, str]:
    """Return trajectory choices that are actually available for one year."""
    return get_year_config(year)["trajectory_sources"]


def dataset_available(year: int, key: str) -> bool:
    """Return whether a CSV dataset or image collection exists for one year."""
    config = get_year_config(year)
    if key == "images":
        return bool(config.get("base_url_images"))
    return key in config["csv_files"]


BASE_URL_CSV = YEAR_CONFIGS[DEFAULT_YEAR]["base_url_csv"]
BASE_URL_IMAGES = YEAR_CONFIGS[DEFAULT_YEAR]["base_url_images"]
CSV_FILES = YEAR_CONFIGS[DEFAULT_YEAR]["csv_files"]
TRAJECTORY_SOURCES = YEAR_CONFIGS[DEFAULT_YEAR]["trajectory_sources"]
FLIGHT_EVENTS = YEAR_CONFIGS[DEFAULT_YEAR]["flight_events"]