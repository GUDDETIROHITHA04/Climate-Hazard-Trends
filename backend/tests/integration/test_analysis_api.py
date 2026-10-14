import pytest

URL = "/api/v1/analysis"
POINT = {"lat": 17.4, "lon": 78.5, "start_year": 1995, "end_year": 2020}


def test_health(api):
    assert api.get("/api/v1/health").json() == {"status": "ok"}


def test_heatwave_response_shape(api):
    response = api.get(URL, params=POINT)

    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["yearly"]) == 26
    assert body["trends"]["primary"]["ok"]
    assert body["insights"]["headline"]
    assert body["definition"]["text"].startswith("A heatwave")
    assert body["meta"]["cache_hit"] is False


def test_second_identical_request_is_served_from_mongodb_without_calling_the_provider(api, fake_client):
    api.get(URL, params=POINT)
    second = api.get(URL, params=POINT)

    assert second.json()["meta"]["cache_hit"] is True
    assert len(fake_client.fetch_calls) == 1


def test_nearby_points_share_the_same_grid_cell_cache(api, fake_client):
    api.get(URL, params=POINT)
    api.get(URL, params={**POINT, "lat": 17.42, "lon": 78.48})

    assert len(fake_client.fetch_calls) == 1


def test_city_and_box_regions_work(api):
    city = api.get(URL, params={"city": "Testville", "start_year": 1995, "end_year": 2020})
    box = api.get(URL, params={"south": 16, "west": 77, "north": 18, "east": 79, "start_year": 1995, "end_year": 2020})

    assert city.status_code == 200 and city.json()["region"]["label"] == "Testville, Nowhere"
    assert box.json()["region"]["type"] == "box"


@pytest.mark.parametrize("hazard,min_duration", [("heavy_rainfall", 1), ("drought", 2)])
def test_rainfall_based_hazards(api, hazard, min_duration):
    response = api.get(URL, params={**POINT, "hazard": hazard, "min_duration": min_duration})

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["hazard"] == hazard and len(body["yearly"]) == 26
    assert sum(row["primary"] for row in body["yearly"]) > 0
    assert body["hazard_meta"]["event_columns"][0]["key"] == "start"


def test_rainfall_data_is_shared_between_the_two_rainfall_hazards(api, fake_client):
    api.get(URL, params={**POINT, "hazard": "heavy_rainfall", "min_duration": 1})
    calls_after_first = len(fake_client.fetch_calls)
    api.get(URL, params={**POINT, "hazard": "drought", "min_duration": 2})

    assert len(fake_client.fetch_calls) <= calls_after_first + 1  # drought may widen the range by one year at most
