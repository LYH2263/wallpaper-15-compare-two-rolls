import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.db import connect
from app.main import app
from app.repositories import history
from app.services import estimate_service


def _run_count():
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_compare_reuses_same_engine_as_single():
    cmp = estimate_service.run_compare(1, 1, 2, False, "")
    single_a = estimate_service.run_estimate(1, 1, False, "")
    single_b = estimate_service.run_estimate(1, 2, False, "")
    for key in ("drops", "drop_len_m", "pattern_m", "strips_per_roll", "rolls"):
        assert cmp["side_a"][key] == single_a[key]
        assert cmp["side_b"][key] == single_b[key]
    assert cmp["delta_rolls"] == single_b["rolls"] - single_a["rolls"]


def test_compare_both_sides_and_delta():
    out = estimate_service.run_compare(1, 1, 2, False, "")
    assert out["mode"] == "compare"
    assert out["side_a"]["rolls"] == 11
    assert out["side_b"]["rolls"] == 16
    assert out["side_b"]["drops"] == out["side_a"]["drops"] == 31
    assert out["delta_rolls"] == 5
    assert out["run_id"] is None


@pytest.mark.parametrize(
    "wall_id,roll_a,roll_b,status",
    [
        (1, 1, 1, 422),  # same roll twice
        (1, 1, 99, 404),  # roll b missing
        (1, 99, 1, 404),  # roll a missing
        (99, 1, 2, 404),  # wall missing
        (1, 1, 3, 422),  # roll b dirty
        (1, 3, 1, 422),  # roll a dirty
        (3, 1, 2, 422),  # wall dirty
    ],
)
def test_compare_rejected_adds_no_row(wall_id, roll_a, roll_b, status):
    before = _run_count()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_compare(wall_id, roll_a, roll_b, True, "")
    assert exc.value.status_code == status
    assert _run_count() == before


def test_compare_save_inserts_single_row_with_both_rolls():
    before = _run_count()
    out = estimate_service.run_compare(2, 1, 2, True, "对照")
    assert _run_count() == before + 1
    run = history.get_run(out["run_id"])
    assert run["roll_id"] == 1
    assert run["roll_id_b"] == 2
    result = run["result"]
    assert result["mode"] == "compare"
    assert result["roll_a"]["id"] == 1 and result["roll_a"]["name"]
    assert result["roll_b"]["id"] == 2 and result["roll_b"]["name"]
    assert result["side_a"]["rolls"] == 13
    assert result["side_b"]["rolls"] == 19
    assert result["delta_rolls"] == 6


def test_saved_compare_not_recomputed_after_pattern_change():
    out = estimate_service.run_compare(1, 1, 2, True, "")
    run_id = out["run_id"]
    conn = connect()
    try:
        conn.execute("UPDATE rolls SET pattern_cm=200 WHERE id=2")
        conn.commit()
    finally:
        conn.close()
    try:
        saved = history.get_run(run_id)["result"]
        assert saved["roll_b"]["pattern_cm"] == 64
        assert saved["side_b"]["drop_len_m"] == 3.34
        assert saved["side_b"]["rolls"] == 16
        assert saved["delta_rolls"] == 5
    finally:
        conn = connect()
        try:
            conn.execute("UPDATE rolls SET pattern_cm=64 WHERE id=2")
            conn.commit()
        finally:
            conn.close()


def test_single_path_unchanged():
    out = estimate_service.run_estimate(1, 1, False, "")
    assert "mode" not in out
    assert "side_a" not in out
    assert out["rolls"] == 11
    assert out["drops"] == 31


def test_single_save_row_has_no_roll_id_b():
    out = estimate_service.run_estimate(1, 1, True, "")
    run = history.get_run(out["run_id"])
    assert run["roll_id_b"] is None
    assert run["result"]["rolls"] == 11


def test_api_compare_and_single_branch():
    with TestClient(app) as client:
        r = client.post("/api/estimate", json={"wall_id": 1, "roll_id": 1, "roll_id_b": 2})
        assert r.status_code == 200
        body = r.json()
        assert body["mode"] == "compare"
        assert body["delta_rolls"] == 5

        r = client.post("/api/estimate", json={"wall_id": 1, "roll_id": 1, "roll_id_b": 1})
        assert r.status_code == 422

        r = client.post("/api/estimate", json={"wall_id": 1, "roll_id": 1})
        assert r.status_code == 200
        body = r.json()
        assert "mode" not in body
        assert body["rolls"] == 11

        r = client.get("/api/estimate", params={"wall_id": 1, "roll_id": 1, "roll_id_b": 2})
        assert r.status_code == 200
        assert r.json()["mode"] == "compare"


def test_api_saved_compare_detail_roundtrip():
    with TestClient(app) as client:
        r = client.post(
            "/api/estimate",
            json={"wall_id": 1, "roll_id": 1, "roll_id_b": 2, "save": True, "note": "对照"},
        )
        assert r.status_code == 200
        run_id = r.json()["run_id"]

        r = client.get(f"/api/runs/{run_id}")
        assert r.status_code == 200
        run = r.json()
        assert run["roll_id"] == 1
        assert run["roll_id_b"] == 2
        assert run["result"]["mode"] == "compare"
        assert run["result"]["side_a"]["rolls"] == 11
        assert run["result"]["side_b"]["rolls"] == 16

        r = client.get("/api/runs/999999")
        assert r.status_code == 404
