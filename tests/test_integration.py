import pytest

from src.sensor_integration import (
    apply_assignment_5_1_filter,
    process_reading,
    validate_sensor_reading,
)


def make_row(temp, unit="C", status="OK"):
    return {
        "record_id": "test",
        "run_id": "test",
        "sample_number": "1",
        "raw_adc": "512",
        "temperature_c": temp,
        "unit": unit,
        "sensor_status": status,
    }


def test_normal_sensor_reading():
    result, _ = process_reading(make_row("25.0"), "VX-200")
    assert result["accepted_status"] == "ACCEPTED"
    assert result["engineering_status"] == "CALCULATED"
    assert float(result["engineering_coefficient"]) == pytest.approx(1.16)


def test_normal_variation():
    result, _ = process_reading(make_row("26.0"), "VX-200", previous_numeric=25.0)
    assert result["validation_decision"] == "VALID"
    assert result["accepted_status"] == "ACCEPTED"


def test_sensor_lower_boundary_is_accepted_by_sensor_filter():
    result, _ = process_reading(make_row("0.0"), "VX-200")
    assert result["filter_decision"] == "ACCEPT"
    assert result["accepted_value_c"] == 0.0
    assert result["engineering_status"] == "REJECTED_BY_ENGINEERING_TOOL"


def test_sensor_upper_boundary_is_accepted_and_used():
    result, _ = process_reading(make_row("50.0"), "VX-200")
    assert result["filter_decision"] == "ACCEPT"
    assert result["engineering_status"] == "CALCULATED"
    assert float(result["engineering_coefficient"]) == pytest.approx(1.27)


def test_out_of_range_value_is_rejected_before_engineering_tool():
    result, _ = process_reading(make_row("54.1", status="OUT_OF_RANGE"), "VX-200")
    assert result["filter_decision"] == "REJECT_RANGE"
    assert result["engineering_status"] == "NOT_RUN"


def test_suspicious_spike_is_flagged():
    result, _ = process_reading(make_row("49.0"), "VX-200", previous_numeric=25.0)
    assert result["validation_decision"] == "VALID_WITH_WARNING"
    assert result["spike_flag"] == "True"
    assert result["accepted_status"] == "ACCEPTED"


def test_missing_reading_is_rejected_and_not_invented():
    result, _ = process_reading(make_row("", status="SIMULATED_MISSING"), "VX-200")
    assert result["accepted_status"] == "REJECTED"
    assert result["accepted_value_c"] == ""
    assert result["value_used_c"] == ""
    assert result["engineering_status"] == "NOT_RUN"


def test_non_numeric_reading_is_rejected():
    numeric, decision, reason, _ = validate_sensor_reading("bad", "C")
    assert numeric is None
    assert decision == "INVALID"
    accepted, filter_decision, accepted_value = apply_assignment_5_1_filter(numeric)
    assert accepted is False
    assert filter_decision == "REJECT_MISSING_OR_INVALID"
    assert accepted_value is None


def test_unexpected_unit_is_rejected():
    result, _ = process_reading(make_row("25.0", unit="F"), "VX-200")
    assert result["accepted_status"] == "REJECTED"
    assert "unexpected unit" in result["validation_reason"]


def test_valid_sensor_reading_flows_through_original_engineering_calculation():
    result, _ = process_reading(make_row("27.0"), "VX-200")
    assert result["engineering_status"] == "CALCULATED"
    assert result["engineering_method"] == "interpolation"
    assert float(result["engineering_coefficient"]) == pytest.approx(1.168)
