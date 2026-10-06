"""Sensor-to-tool integration for EGN321 Assignment 5.2.

Flow:
Raw sensor reading -> validation -> 5.1 filtering/rejection ->
accepted value -> original Module 3 engineering tool -> result.
"""

import csv
import math
from pathlib import Path

from src.selection_tool import select_coefficient

SENSOR_MIN_C = 0.0
SENSOR_MAX_C = 50.0
EXPECTED_UNIT = "C"
SPIKE_THRESHOLD_C = 20.0


def validate_sensor_reading(raw_temperature, unit, previous_numeric=None):
    """Validate a raw temperature before filtering or engineering use.

    Returns (numeric_value_or_none, decision, reason, spike_flag).
    A suspicious spike is flagged for traceability but is not rejected by
    itself because Assignment 5.1 defined the actual rejection rule as
    missing/non-numeric/non-finite or outside 0-50 °C.
    """
    if raw_temperature is None or str(raw_temperature).strip() == "":
        return None, "INVALID", "missing temperature", False

    if unit != EXPECTED_UNIT:
        return None, "INVALID", f"unexpected unit: {unit!r}", False

    try:
        value = float(raw_temperature)
    except (TypeError, ValueError):
        return None, "INVALID", "non-numeric temperature", False

    if not math.isfinite(value):
        return None, "INVALID", "non-finite temperature", False

    spike = (
        previous_numeric is not None
        and abs(value - previous_numeric) > SPIKE_THRESHOLD_C
    )
    if spike:
        return value, "VALID_WITH_WARNING", "suspicious spike", True

    return value, "VALID", "numeric Celsius reading", False


def apply_assignment_5_1_filter(value):
    """Apply the exact Assignment 5.1 rejection/filtering rule."""
    if value is None:
        return False, "REJECT_MISSING_OR_INVALID", None
    if value < SENSOR_MIN_C or value > SENSOR_MAX_C:
        return False, "REJECT_RANGE", None
    return True, "ACCEPT", value


def process_reading(row, valve_family="VX-200", previous_numeric=None):
    raw_temperature = row.get("temperature_c", "")
    unit = row.get("unit", "")

    numeric, validation_decision, validation_reason, spike = validate_sensor_reading(
        raw_temperature, unit, previous_numeric
    )
    accepted, filter_decision, accepted_value = apply_assignment_5_1_filter(numeric)

    result = {
        "record_id": row.get("record_id", ""),
        "run_id": row.get("run_id", ""),
        "sample_number": row.get("sample_number", ""),
        "raw_adc": row.get("raw_adc", ""),
        "raw_temperature_c": raw_temperature,
        "raw_unit": unit,
        "sensor_status": row.get("sensor_status", ""),
        "validation_decision": validation_decision,
        "validation_reason": validation_reason,
        "spike_flag": str(spike),
        "filter_decision": filter_decision,
        "accepted_status": "ACCEPTED" if accepted else "REJECTED",
        "accepted_value_c": "" if accepted_value is None else accepted_value,
        "value_used_c": "" if accepted_value is None else accepted_value,
        "engineering_status": "NOT_RUN",
        "engineering_reason": "sensor reading rejected before engineering calculation",
        "valve_family": valve_family,
        "engineering_coefficient": "",
        "engineering_method": "",
    }

    if accepted:
        try:
            engineering = select_coefficient(valve_family, accepted_value)
        except (ValueError, TypeError) as exc:
            result["engineering_status"] = "REJECTED_BY_ENGINEERING_TOOL"
            result["engineering_reason"] = str(exc)
        else:
            result["engineering_status"] = "CALCULATED"
            result["engineering_reason"] = "accepted sensor value used by original tool"
            result["engineering_coefficient"] = engineering["coefficient"]
            result["engineering_method"] = engineering["method"]

    return result, numeric


def replay_csv(input_path, output_path, valve_family="VX-200"):
    """Replay sensor records one at a time and write a traceability log."""
    input_path = Path(input_path)
    output_path = Path(output_path)

    previous_numeric = None
    rows_out = []

    with input_path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        for row in reader:
            result, numeric = process_reading(
                row, valve_family=valve_family, previous_numeric=previous_numeric
            )
            rows_out.append(result)
            if numeric is not None:
                previous_numeric = numeric

    if rows_out:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows_out[0].keys()))
            writer.writeheader()
            writer.writerows(rows_out)

    return rows_out
