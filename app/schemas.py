# app/schemas.py

from pydantic import BaseModel

class RaceInput(BaseModel):
    year: int
    grand_prix: str

    class Config:
        from_attributes = True
