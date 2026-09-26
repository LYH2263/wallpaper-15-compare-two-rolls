import os
import tempfile

os.environ["DATA_DIR"] = tempfile.mkdtemp(prefix="wp-compare-test-")

from fastapi.testclient import TestClient

from app.db import connect
from app.main import app
from app import seed

seed.init_db()
client = TestClient(app)

# seed: wall 2 = (perimeter 20, height 2.8); roll 1 = 素色53 (0.53/10/0); roll 2 = 大花64 (0.53/10/64)
WALL = 2
ROLL_A = 1
ROLL_B = 2


def run_count():
    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_compare_both_sides_and_delta():
    r = client.get(f"/api/estimate?wall_id={WALL}&roll_id={ROLL_A}&roll_id_b={ROLL_B}")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "compare"
    assert body["roll"]["id"] == ROLL_A
    assert body["roll_b"]["id"] == ROLL_B
    assert body["a"] == {"drops": 38, "drop_len_m": 2.8, "pattern_m": 0.0, "strips_per_roll": 3, "rolls": 13}
    assert body["b"] == {"drops": 38, "drop_len_m": 3.44, "pattern_m": 0.64, "strips_per_roll": 2, "rolls": 19}
    assert body["delta_rolls"] == 6
    assert body["run_id"] is None


def test_compare_save_single_row_with_both_rolls():
    before = run_count()
    r = client.post("/api/estimate", json={"wall_id": WALL, "roll_id": ROLL_A, "roll_id_b": ROLL_B, "save": True})
    assert r.status_code == 200
    run_id = r.json()["run_id"]
    assert run_id is not None
    assert run_count() == before + 1

    detail = client.get(f"/api/runs/{run_id}")
    assert detail.status_code == 200
    result = detail.json()["result"]
    assert result["mode"] == "compare"
    assert result["roll_id_a"] == ROLL_A
    assert result["roll_id_b"] == ROLL_B
    assert result["a"]["rolls"] == 13
    assert result["b"]["rolls"] == 19
    assert result["delta_rolls"] == 6


def test_single_roll_behaviour_unchanged():
    before = run_count()
    r = client.post("/api/estimate", json={"wall_id": WALL, "roll_id": ROLL_A, "save": True})
    assert r.status_code == 200
    body = r.json()
    assert "mode" not in body
    assert body["rolls"] == 13
    assert body["drops"] == 38
    assert run_count() == before + 1

    result = client.get(f"/api/runs/{body['run_id']}").json()["result"]
    assert result.get("mode") != "compare"
    assert result["roll_id"] == ROLL_A
    assert result["rolls"] == 13


def test_compare_rejects_same_roll_without_saving():
    before = run_count()
    r = client.post("/api/estimate", json={"wall_id": WALL, "roll_id": ROLL_A, "roll_id_b": ROLL_A, "save": True})
    assert r.status_code == 422
    assert run_count() == before


def test_compare_rejects_missing_roll_without_saving():
    before = run_count()
    r = client.post("/api/estimate", json={"wall_id": WALL, "roll_id": ROLL_A, "roll_id_b": 999, "save": True})
    assert r.status_code == 404
    assert run_count() == before


def test_compare_rejects_dirty_entities_without_saving():
    dirty_wall = 3
    dirty_roll = 3
    for wall_id, roll_id, roll_id_b in [
        (dirty_wall, ROLL_A, ROLL_B),
        (WALL, dirty_roll, ROLL_B),
        (WALL, ROLL_A, dirty_roll),
    ]:
        before = run_count()
        r = client.post("/api/estimate", json={"wall_id": wall_id, "roll_id": roll_id, "roll_id_b": roll_id_b, "save": True})
        assert r.status_code == 422
        assert run_count() == before


def test_saved_compare_not_recomputed_after_pattern_change():
    r = client.post("/api/estimate", json={"wall_id": WALL, "roll_id": ROLL_A, "roll_id_b": ROLL_B, "save": True})
    run_id = r.json()["run_id"]

    conn = connect()
    try:
        conn.execute("UPDATE rolls SET pattern_cm=128 WHERE id=?", (ROLL_B,))
        conn.commit()
    finally:
        conn.close()

    result = client.get(f"/api/runs/{run_id}").json()["result"]
    assert result["b"]["pattern_m"] == 0.64
    assert result["b"]["rolls"] == 19
    assert result["delta_rolls"] == 6
