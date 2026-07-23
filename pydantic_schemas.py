from pydantic import BaseModel
from typing import Dict, List

class UniqueDropPayLoad(BaseModel): 
    instance_id: int
    area_name: str
    uniques: Dict[str, tuple[str, str]]
    
class MapAnalyticsRow(BaseModel):
    map_name: str
    updated_at: str
    total_uniques: int
    t0_uniques: dict[str, int]  
    t1_uniques: dict[str, int]  

class FullAnalyticsResponse(BaseModel):
    grand_total: int
    t0_grand_total: dict[str, int]  
    t1_grand_total: dict[str, int]  
    rows: list[MapAnalyticsRow]