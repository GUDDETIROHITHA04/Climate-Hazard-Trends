import pytest

URL = "/api/v1/analysis"
BASE = {"lat": 17.4, "lon": 78.5, "start_year": 1995, "end_year": 2020}


@pytest.mark.parametrize(
    "params",
    [
        {"lat": 123, "lon": 0},                                                   # latitude out of range
        {"lat": 10},                                                              # longitude missing
        {},                                                                       # no region at all
        {"lat": 10, "lon": 10, "city": "Hyderabad"},                              # two region modes
        {"city": "x; DROP TABLE", "start_year": 1995, "end_year": 2020},          # suspicious text
        {"south": 0, "west": 0, "north": 20, "east": 20},                         # box too large
        {"south": 10, "west": 10, "north": 5, "east": 20},                        # south above north
        {**BASE, "hazard": "flood"},                                              # unknown hazard
        {**BASE, "start_year": 2018, "end_year": 2020},                           # fewer than 10 years
        {**BASE, "start_year": 2020, "end_year": 1995},                           # reversed range
        {**BASE, "percentile": 50},                                               # percentile out of range
        {**BASE, "method": "nope"},                                               # unknown method
        {**BASE, "unexpected": "value"},                                          # unknown parameter
        {**BASE, "min_duration": 1},                                              # heatwave needs 2+ days
    ],
)
def test_invalid_requests_are_rejected_with_422(api, params):
    assert api.get(URL, params=params).status_code == 422
