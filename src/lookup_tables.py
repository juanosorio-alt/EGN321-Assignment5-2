"""
EGN 321 — Module 3, Assignment 3.1
Lookup table data.

Each pair contains: (temperature_c, coefficient).
Temperatures are sorted from lowest to highest.
"""

LOOKUP_TABLES = {
    "VX-100": [
        (20, 0.88),
        (40, 0.93),
        (60, 0.99),
        (80, 1.06),
        (100, 1.14),
    ],
    "VX-200": [
        (10, 1.10),
        (30, 1.18),
        (50, 1.27),
        (70, 1.39),
        (90, 1.54),
    ],
    "VX-300": [
        (25, 1.42),
        (50, 1.55),
        (75, 1.71),
        (100, 1.90),
        (125, 2.12),
    ],
}
