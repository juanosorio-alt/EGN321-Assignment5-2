"""
Validated valve coefficient lookup with linear interpolation.

This file preserves the original engineering logic from Module 3,
Assignment 3.1. Sensor handling is intentionally kept in a separate layer.
"""

from src.interpolation import linear_interpolate
from src.lookup_tables import LOOKUP_TABLES


def select_coefficient(valve_family, temperature_c):
    if valve_family not in LOOKUP_TABLES:
        raise ValueError(f"Unsupported valve family: {valve_family}")

    table = LOOKUP_TABLES[valve_family]
    minimum_temp = table[0][0]
    maximum_temp = table[-1][0]

    if temperature_c < minimum_temp:
        raise ValueError(
            f"temperature_c {temperature_c} is below "
            f"the supported minimum {minimum_temp}"
        )

    if temperature_c > maximum_temp:
        raise ValueError(
            f"temperature_c {temperature_c} exceeds "
            f"the supported maximum {maximum_temp}"
        )

    for table_temp, coefficient in table:
        if temperature_c == table_temp:
            return {
                "valve_family": valve_family,
                "temperature_c": temperature_c,
                "coefficient": coefficient,
                "method": "exact",
                "lower_point": (table_temp, coefficient),
                "upper_point": (table_temp, coefficient),
                "supported_range": (minimum_temp, maximum_temp),
            }

    for i in range(len(table) - 1):
        x1, y1 = table[i]
        x2, y2 = table[i + 1]

        if x1 < temperature_c < x2:
            coefficient = linear_interpolate(
                temperature_c, x1, y1, x2, y2
            )
            return {
                "valve_family": valve_family,
                "temperature_c": temperature_c,
                "coefficient": coefficient,
                "method": "interpolation",
                "lower_point": (x1, y1),
                "upper_point": (x2, y2),
                "supported_range": (minimum_temp, maximum_temp),
            }

    raise ValueError("No valid table interval found.")
