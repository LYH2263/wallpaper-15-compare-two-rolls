from pydantic import BaseModel


class EstimateRequest(BaseModel):
    wall_id: int
    roll_id: int
    roll_id_b: int | None = None
    save: bool = False
    note: str = ""
