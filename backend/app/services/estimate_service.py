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
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll_a = rolls.get_roll(roll_id_a)
    if not roll_a:
        raise HTTPException(404, "roll not found")
    roll_b = rolls.get_roll(roll_id_b)
    if not roll_b:
        raise HTTPException(404, "roll not found")
    if roll_id_a == roll_id_b:
        raise HTTPException(422, "compare needs two different rolls")
    if any(e.get("data_quality") == "dirty" for e in (wall, roll_a, roll_b)):
        raise HTTPException(422, "dirty seed entity")

    calc_a = roll_count(
        wall["perimeter"], wall["height"], roll_a["width"], roll_a["length"], roll_a["pattern_cm"]
    )
    calc_b = roll_count(
        wall["perimeter"], wall["height"], roll_b["width"], roll_b["length"], roll_b["pattern_cm"]
    )
    delta_rolls = abs(calc_a["rolls"] - calc_b["rolls"])
    snapshot = {
        "mode": "compare",
        "wall_id": wall_id,
        "roll_id_a": roll_id_a,
        "roll_id_b": roll_id_b,
        "roll_name_a": roll_a["name"],
        "roll_name_b": roll_b["name"],
        "a": calc_a,
        "b": calc_b,
        "delta_rolls": delta_rolls,
    }
    run_id = None
    if save:
        run_id = history.insert_run(wall_id, roll_id_a, snapshot, note)
    return {
        "wall": wall,
        "roll": roll_a,
        "roll_b": roll_b,
        "run_id": run_id,
        "mode": "compare",
        "a": calc_a,
        "b": calc_b,
        "delta_rolls": delta_rolls,
    }
