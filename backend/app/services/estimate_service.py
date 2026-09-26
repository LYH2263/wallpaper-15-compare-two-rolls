from fastapi import HTTPException

from app.engines.wallpaper_math import roll_count
from app.repositories import history, rolls, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    calc = roll_count(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )
    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id, {**calc, "wall_id": wall_id, "roll_id": roll_id}, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **calc}


def run_compare(wall_id: int, roll_id_a: int, roll_id_b: int, save: bool, note: str):
    if roll_id_a == roll_id_b:
        raise HTTPException(422, "compare requires two different rolls")
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll_a = rolls.get_roll(roll_id_a)
    roll_b = rolls.get_roll(roll_id_b)
    if not roll_a or not roll_b:
        raise HTTPException(404, "roll not found")
    if (
        wall.get("data_quality") == "dirty"
        or roll_a.get("data_quality") == "dirty"
        or roll_b.get("data_quality") == "dirty"
    ):
        raise HTTPException(422, "dirty seed entity")

    side_a = roll_count(
        wall["perimeter"], wall["height"], roll_a["width"], roll_a["length"], roll_a["pattern_cm"]
    )
    side_b = roll_count(
        wall["perimeter"], wall["height"], roll_b["width"], roll_b["length"], roll_b["pattern_cm"]
    )
    delta_rolls = side_b["rolls"] - side_a["rolls"]
    run_id = None
    if save:
        snapshot = {
            "mode": "compare",
            "wall_id": wall_id,
            "roll_id": roll_id_a,
            "roll_id_b": roll_id_b,
            "roll_a": _roll_snapshot(roll_a),
            "roll_b": _roll_snapshot(roll_b),
            "side_a": side_a,
            "side_b": side_b,
            "delta_rolls": delta_rolls,
        }
        run_id = history.insert_run(wall_id, roll_id_a, snapshot, note, roll_id_b=roll_id_b)
    return {
        "mode": "compare",
        "wall": wall,
        "roll_a": roll_a,
        "roll_b": roll_b,
        "run_id": run_id,
        "side_a": side_a,
        "side_b": side_b,
        "delta_rolls": delta_rolls,
    }


def _roll_snapshot(roll: dict) -> dict:
    return {k: roll[k] for k in ("id", "name", "width", "length", "pattern_cm")}
