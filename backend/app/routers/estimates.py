from fastapi import APIRouter, Query
from app.schemas.estimate import EstimateRequest
from app.services import estimate_service

router = APIRouter()


@router.get("/estimate")
def estimate_get(
    wall_id: int = Query(...),
    roll_id: int = Query(...),
    roll_id_b: int | None = Query(None),
    save: bool = False,
):
    if roll_id_b is None:
        return estimate_service.run_estimate(wall_id, roll_id, save, "")
    return estimate_service.run_compare(wall_id, roll_id, roll_id_b, save, "")


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    if body.roll_id_b is None:
        return estimate_service.run_estimate(body.wall_id, body.roll_id, body.save, body.note)
    return estimate_service.run_compare(body.wall_id, body.roll_id, body.roll_id_b, body.save, body.note)
