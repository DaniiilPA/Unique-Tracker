from pydantic_schemas import MapAnalyticsRow, FullAnalyticsResponse
from depends import MapDrop
T0_ITEMS = ["headhunter"]
T1_ITEMS = []

def transform_db_records_to_analytics(records: list[MapDrop]) -> FullAnalyticsResponse:
    analytics_rows = []
    grand_total = 0
    
    for record in records:
        uniques_dict: dict = record.uniques
        
        t0 = {}
        t1 = {}
        total_count = len(uniques_dict)
        
        for item_id, item_info in uniques_dict.items():
            item_name = item_info[1]
            
            if item_name in T0_ITEMS:
                t0[item_name] = t0.get(item_name, 0) + 1
            elif item_name in T0_ITEMS:
                t0[item_name] = t0.get(item_name, 0) + 1
                
        analytics_rows.append(
            MapAnalyticsRow(
                map_name=record.area_name,
                updated_at=record.updated_at.strftime("%d.%m.%Y %H:%M"),
                total_uniques=total_count,
                t0_uniques=t0,
                t1_uniques=t1
            )
        )
        grand_total += total_count
        
    return FullAnalyticsResponse(rows=analytics_rows, grand_total=grand_total)