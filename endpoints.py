from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from fastapi.concurrency import run_in_threadpool

from pydantic_schemas import UniqueDropPayLoad
from analyzer import transform_db_records_to_analytics
from depends import get_db, MapDrop, save_or_merge_drops, get_all_uniques
from security import verify_api_key

router = APIRouter()

@router.get("/api/stats/")
async def give_stats(maps: int, db: AsyncSession = Depends(get_db), _ : str = Security(verify_api_key)):
    try:
        records = await get_all_uniques(db=db, maps_num=maps)
        
        payload = await run_in_threadpool(
            transform_db_records_to_analytics, records
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
@router.post("/api/drops/")
async def receive_drops(data: UniqueDropPayLoad, db: AsyncSession = Depends(get_db), _ : str = Security(verify_api_key)):
    try:    
        await save_or_merge_drops(db=db, 
                                instance_id=data.instance_id, 
                                area_name=data.area_name, 
                                uniques_dict=data.uniques
                                )
        
        await db.commit()
        
        return {"status": "success", "num": len(data.uniques)}
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"database error: {str(e)}")
