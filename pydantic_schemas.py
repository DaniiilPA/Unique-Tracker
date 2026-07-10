from pydantic import BaseModel
from typing import Dict, List

class UniqueDropPayLoad(BaseModel): 
    instance_id: int
    area_name: str
    uniques: Dict[str, List[str]]
    
class MapAnalyticsRow(BaseModel):
    map_name: str
    updated_at: str
    total_uniques: int
    t0_uniques: dict[str, int]  
    t1_uniques: dict[str, int]  

class FullAnalyticsResponse(BaseModel):
    rows: list[MapAnalyticsRow]
    grand_total: int