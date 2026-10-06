"""
Linear interpolation helpers.

Preserved from EGN321 Module 3, Assignment 3.1.
"""


def linear_interpolate(x, x1, y1, x2, y2):
    """
    Return y at x between points (x1, y1) and (x2, y2).

    Range validation belongs in the lookup/selection layer.
    """
    if x1 == x2:
        raise ValueError("The two temperatures must be different.")

    return y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)
