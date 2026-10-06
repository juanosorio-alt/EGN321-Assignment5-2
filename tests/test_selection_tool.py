import pytest
from src.selection_tool import select_coefficient


def test_exact_lookup_vx200():
    result = select_coefficient("VX-200", 90)
    assert result["coefficient"] == 1.54
    assert result["method"] == "exact"


def test_interpolation_vx100():
    result = select_coefficient("VX-100", 50)
    assert result["coefficient"] == pytest.approx(0.96)
    assert result["method"] == "interpolation"


def test_lower_boundary_accepted():
    result = select_coefficient("VX-100", 20)
    assert result["coefficient"] == 0.88


def test_below_range_refused():
    with pytest.raises(ValueError, match="supported minimum"):
        select_coefficient("VX-100", 5)


def test_unknown_family_refused():
    with pytest.raises(ValueError, match="Unsupported valve family"):
        select_coefficient("VX-999", 50)
