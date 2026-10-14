def test_list_states(api):
    response = api.get("/api/v1/regions", params={"type": "state"})

    assert response.status_code == 200
    names = [r["name"] for r in response.json()]
    assert "Telangana" in names and len(names) >= 28


def test_list_cities_is_the_default(api):
    response = api.get("/api/v1/regions")

    assert any(r["name"] == "Hyderabad" for r in response.json())


def test_invalid_region_type_is_rejected(api):
    assert api.get("/api/v1/regions", params={"type": "country"}).status_code == 422


def test_place_search(api):
    response = api.get("/api/v1/regions/search", params={"q": "Testville"})

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Testville, Nowhere"


def test_place_search_rejects_short_or_unsafe_text(api):
    assert api.get("/api/v1/regions/search", params={"q": "a"}).status_code == 422
    assert api.get("/api/v1/regions/search", params={"q": "<script>"}).status_code == 422


def test_city_list_is_filtered_by_selected_state(api):
    response = api.get("/api/v1/regions", params={"type": "city", "state": "Telangana"})

    assert response.status_code == 200
    names = [city["name"] for city in response.json()]
    assert names
    assert "Hyderabad" in names
    assert all(city["state"] == "Telangana" for city in response.json())
