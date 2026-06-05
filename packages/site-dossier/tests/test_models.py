import pytest
from site_dossier.models import SiteInput


def test_address_only_is_valid():
    s = SiteInput(address="350 5th Ave, NY")
    assert s.as_query() == "350 5th Ave, NY"


def test_lat_lon_only_is_valid():
    s = SiteInput(lat=40.7, lon=-74.0)
    assert s.as_query() == "40.7,-74.0"


def test_neither_raises():
    with pytest.raises(ValueError):
        SiteInput()


def test_out_of_range_raises():
    with pytest.raises(ValueError):
        SiteInput(lat=100.0, lon=0.0)
    with pytest.raises(ValueError):
        SiteInput(lat=0.0, lon=-200.0)
