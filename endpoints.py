from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Security, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic_schemas import UniqueDropPayLoad, FullAnalyticsResponse
from analyzer import transform_db_records_to_analytics
from depends import get_db, save_or_merge_drops
from security import verify_api_key

router = APIRouter()

@router.get("/api/stats", response_model=FullAnalyticsResponse)
async def give_stats(
    maps: int = Query(..., ge=0),
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
    _: str = Security(verify_api_key)
):
    try:
        return await transform_db_records_to_analytics(
            db=db,
            maps_num=maps,
            date_from=date_from,
            date_to=date_to
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@router.post("/api/drops")
async def receive_drops(data: UniqueDropPayLoad, db: AsyncSession = Depends(get_db), _: str = Security(verify_api_key)):
    try:    
        await save_or_merge_drops(
            db=db, 
            instance_id=data.instance_id, 
            area_name=data.area_name, 
            uniques_dict=data.uniques
        )
        await db.commit()
        return {"status": "success", "num": len(data.uniques)}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"database error: {str(e)}")
