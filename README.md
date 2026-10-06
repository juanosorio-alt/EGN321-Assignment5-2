# EGN321 Assignment 5.2 — Feed the Tool

**Student:** Juan Osorio  
**Project:** Replace Typed Input with Virtual Sensor Data

## Project Overview

This project integrates the virtual NTC temperature sensor from Assignment 5.1 with the valve coefficient lookup tool from Module 3, Assignment 3.1.

The original engineering tool expected a temperature value to already be available as a clean program input. Assignment 5.2 changes that assumption: temperature now comes from replayed virtual-sensor data and must pass validation and filtering before the original engineering calculation is allowed to run.

The integration method used is **Option A — CSV Replay**, the recommended method in the assignment.

## Integration Flow

`Velxio NTC Sensor -> CSV Raw Reading -> Validation -> Assignment 5.1 Filtering -> Accepted/Rejected -> Original Valve Lookup Tool -> Engineering Result`

The main traceability evidence is written to:

`output/integration_log.csv`

That file shows the required chain:

`Raw Sensor Reading -> Validation Decision -> Accepted/Rejected Status -> Value Used -> Engineering Result`

## Existing Engineering Tool

The existing tool is the Module 3, Assignment 3.1 valve coefficient lookup tool.

It selects a coefficient using:

1. valve family;
2. operating temperature in degrees Celsius;
3. exact lookup when a table temperature matches;
4. linear interpolation when the temperature falls between two table rows;
5. refusal when the temperature is outside the selected valve family's supported engineering range.

The original engineering files are preserved in:

- `src/selection_tool.py`
- `src/interpolation.py`
- `src/lookup_tables.py`

The sensor integration was added separately in `src/sensor_integration.py` so the previously verified engineering logic is not rewritten.

## Virtual Sensor Source

The sensor is a virtual NTC temperature sensor connected to an Arduino Uno in Velxio.

Velxio project:
https://velxio.dev/juan-osorio/temperature-lab-correctedvlx/

The Assignment 5.1 sensor output recorded raw ADC values and temperature in degrees Celsius.

## Sensor Dataset / Input File

The primary replay input is:

`data/readings_failure_scenario.csv`

It contains 125 records and includes the simulated missing-data case from Assignment 5.1.

For explicit Assignment 5.2 test coverage, `data/test_sensor_cases.csv` contains normal, normal-variation, boundary, out-of-range, suspicious-spike, missing, and valid-through-calculation examples.

## Sensor Validation Logic

Every reading is checked before it can reach the engineering tool.

Validation checks:

- missing temperature;
- unexpected unit;
- non-numeric value;
- non-finite value;
- suspicious jump greater than 20 °C from the previous numeric sample.

A suspicious spike is recorded as `VALID_WITH_WARNING`. It is not automatically rejected by the spike check because the Assignment 5.1 rejection rule was based on availability, numeric validity, and the 0–50 °C application interval. This keeps the 5.1 filtering rule intact while still documenting spike behavior.

## Filtering / Rejection Rule from Assignment 5.1

The Assignment 5.1 rule is preserved:

- accept temperatures from **0 °C through 50 °C inclusive**;
- reject missing, non-numeric, or non-finite temperatures;
- reject temperatures below 0 °C or above 50 °C;
- never replace a missing reading with zero or silently invent a sensor value;
- retain the raw value and rejection reason for traceability.

### Why this rule is used

Assignment 5.1 defined 0–50 °C as the application's acceptable operating interval. It is an application rule, not the physical limit of the NTC sensor.

### When a value is accepted

A reading is accepted when it is present, numeric, finite, in Celsius, and between 0 °C and 50 °C inclusive.

### When a value is rejected

A reading is rejected when it is missing/invalid or outside 0–50 °C.

### What happens to rejected data

Rejected readings are logged but are **not** passed to the valve coefficient calculation. No replacement value is invented.

## Missing-Input Behavior

If sensor input is unavailable, the program:

1. records the raw missing condition;
2. marks validation as invalid;
3. marks the sensor value as rejected;
4. leaves `accepted_value_c` and `value_used_c` blank;
5. does not execute the engineering calculation for that record;
6. records the reason in the traceability log.

This directly prevents silent fabrication of sensor data.

## Raw and Accepted Values

The trace log keeps separate fields for:

- `raw_temperature_c`
- `validation_decision`
- `validation_reason`
- `filter_decision`
- `accepted_status`
- `accepted_value_c`
- `value_used_c`
- `engineering_status`
- `engineering_coefficient`
- `engineering_method`

This separation makes each decision auditable.

## Sensor Validation vs. Engineering Validation

The two validation layers serve different purposes.

For example, a temperature of 0 °C is accepted by the Assignment 5.1 sensor filter because 0 °C is the lower inclusive sensor boundary. However, with `VX-200`, the original engineering tool rejects 0 °C because the VX-200 lookup table supports 10–90 °C.

This distinction is intentional. Sensor acceptance does not override the original engineering limits.

## Assumptions Broken by Sensor Input

| Original Assumption | What the Sensor Did | Software Change |
|---|---|---|
| A temperature value always exists. | Assignment 5.1 includes a simulated missing reading. | Added explicit missing-value handling and prevented the engineering calculation from running. |
| Temperature input is already numeric and usable. | Sensor/CSV data can be blank, nonnumeric, or non-finite. | Added numeric and finite-value validation before filtering. |
| Temperature arrives in the expected unit. | External sensor data can carry an unexpected unit. | Added a Celsius unit check before accepting the value. |
| A supplied temperature is automatically inside the application's sensor range. | Assignment 5.1 contains readings above 50 °C, including 54.1, 63.0, and 70.0 °C. | Reused the 0–50 °C inclusive rejection rule from Assignment 5.1. |
| Input changes only when a person deliberately edits it. | Sensor records arrive repeatedly, one sample at a time. | Added CSV replay that processes every sensor record independently. |
| Input is stable enough that sudden changes do not need to be recorded. | Sensor sequences can contain abrupt changes. | Added a suspicious-spike flag for changes greater than 20 °C while preserving the 5.1 range rule as the rejection rule. |
| Any accepted sensor value is automatically valid for the engineering table. | A sensor value such as 0 °C can pass the 0–50 °C sensor filter but be outside a valve family's table range. | Preserved the original engineering validation after sensor filtering instead of bypassing it. |

## Required Tests

The automated tests cover at least the cases required by the assignment:

| Required case | Test behavior |
|---|---|
| Normal sensor reading | 25 °C is accepted and produces a VX-200 interpolated coefficient. |
| Normal variation | 26 °C following 25 °C is valid and accepted. |
| Boundary value | 0 °C and 50 °C verify the inclusive Assignment 5.1 sensor boundaries. |
| Out-of-range value | 54.1 °C is rejected before the engineering calculation. |
| Suspicious spike | A jump greater than 20 °C is flagged `VALID_WITH_WARNING`. |
| Missing reading | Blank temperature is rejected and no value is invented. |
| Filtering/rejection case | Values outside 0–50 °C receive `REJECT_RANGE`. |
| Valid reading through original calculation | 27 °C reaches the original VX-200 interpolation logic and produces a coefficient. |

Additional tests cover nonnumeric input and unexpected units.

## Running the Project

From the project root:

```bash
python -m pip install -r requirements.txt
python run_assignment_5_2.py
python -m pytest tests -v
```

The replay script writes:

`output/integration_log.csv`

## Expected Replay Summary

Using the Assignment 5.1 failure-scenario dataset:

- 125 sensor records are processed;
- the range rule rejects the readings above 50 °C;
- the injected missing reading is rejected;
- accepted sensor values are passed to the original valve lookup only when they also satisfy that tool's engineering range.

## Required Deliverables Mapping

1. **Updated engineering tool:** `src/` plus the integration layer.
2. **Virtual sensor source or simulation link:** `SENSOR_SOURCE.md` and this README.
3. **Sensor dataset or input file:** `data/readings_failure_scenario.csv`.
4. **Sensor integration code:** `src/sensor_integration.py` and `run_assignment_5_2.py`.
5. **Updated validation logic:** `validate_sensor_reading()`.
6. **Filtering/rejection logic:** `apply_assignment_5_1_filter()`.
7. **Raw and accepted/rejected log:** `output/integration_log.csv`.
8. **Normal and failure tests:** `tests/test_integration.py` plus preserved original-tool tests.
9. **Updated README:** this file.
10. **Assumptions Broken by Sensor Input:** section above.
11. **GitHub repository URL:** https://github.com/juanosorio-alt/EGN321-Assignment5-2

## GitHub Repository URL

**https://github.com/juanosorio-alt/EGN321-Assignment5-2**

## AI Use

AI assistance was used to help integrate the existing Module 3 engineering tool with the Assignment 5.1 sensor dataset, create validation and traceability logic, prepare tests, and draft documentation. The original Module 3 engineering calculation was preserved rather than replaced.
