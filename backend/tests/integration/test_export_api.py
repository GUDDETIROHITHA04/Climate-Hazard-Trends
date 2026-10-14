URL = "/api/v1/analysis/export"
PARAMS = {"lat": 17.4, "lon": 78.5, "start_year": 1995, "end_year": 2020}


def test_yearly_csv_is_a_downloadable_attachment(api):
    response = api.get(URL, params={**PARAMS, "kind": "yearly"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "attachment" in response.headers["content-disposition"]
    lines = response.text.strip().splitlines()
    assert lines[0].startswith("year,coverage")
    assert len(lines) == 27  # header + 26 years


def test_events_csv_header_matches_hazard_columns(api):
    response = api.get(URL, params={**PARAMS, "kind": "events"})

    assert response.text.startswith("start,end,duration")


def test_unknown_export_kind_is_rejected(api):
    assert api.get(URL, params={**PARAMS, "kind": "pdf"}).status_code == 422
