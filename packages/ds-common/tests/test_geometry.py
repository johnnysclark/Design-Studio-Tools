from ds_common.geometry import cardinal_from_deg, haversine_m, parse_lat_lon


def test_parse_lat_lon_valid():
    assert parse_lat_lon("40.7,-74.0") == (40.7, -74.0)
    assert parse_lat_lon("  -33.9, 151.2 ") == (-33.9, 151.2)


def test_parse_lat_lon_invalid():
    assert parse_lat_lon("not coords") is None
    assert parse_lat_lon("100,0") is None  # out of range
    assert parse_lat_lon("0,200") is None


def test_haversine_zero():
    assert haversine_m(40.0, -74.0, 40.0, -74.0) == 0.0


def test_haversine_known_distance():
    # NYC to Philadelphia ~130 km
    d = haversine_m(40.7128, -74.0060, 39.9526, -75.1652)
    assert 125_000 < d < 135_000


def test_cardinal_from_deg():
    assert cardinal_from_deg(0) == "N"
    assert cardinal_from_deg(90) == "E"
    assert cardinal_from_deg(180) == "S"
    assert cardinal_from_deg(270) == "W"
    assert cardinal_from_deg(45) == "NE"
    assert cardinal_from_deg(360) == "N"
