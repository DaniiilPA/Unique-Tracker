from datetime import date, datetime, time
from typing import AsyncGenerator, Optional
from sqlalchemy import BigInteger, DateTime, func, select, desc, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, insert

from config import settings

ALLOWED_AREAS = ["temple"]

engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class MapDrop(Base):
    __tablename__ = "map_drops"
    
    instance_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    area_name: Mapped[str] = mapped_column(nullable=False)
    uniques: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    
    updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    index=True
    )
    
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    await engine.dispose()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
            yield session
            

async def save_or_merge_drops(db: AsyncSession, instance_id: int, area_name: str, uniques_dict: dict):

    insert_stmt = insert(MapDrop).values(
        instance_id=instance_id,
        area_name=area_name,
        uniques=uniques_dict
    )
        
    upsert_stmt = insert_stmt.on_conflict_do_update(
        index_elements=[MapDrop.instance_id],
        set_={
            "uniques": MapDrop.uniques.concat(insert_stmt.excluded.uniques),
            "updated_at": func.now()
        }
    )
    await db.execute(upsert_stmt)
    
    
SQL_FAST_MAPS_QUERY = text("""
SELECT 
    instance_id,
    area_name,
    to_char(updated_at, 'DD.MM.YYYY HH24:MI') as updated_at_str,
    uniques
FROM map_drops
WHERE (CAST(:start_dt AS TIMESTAMP) IS NULL OR updated_at >= CAST(:start_dt AS TIMESTAMP))
  AND (CAST(:end_dt AS TIMESTAMP) IS NULL OR updated_at <= CAST(:end_dt AS TIMESTAMP))
ORDER BY updated_at DESC
LIMIT CASE WHEN :maps_num > 0 THEN :maps_num ELSE NULL END;
""")

async def stream_raw_maps_from_db(
    db: AsyncSession, 
    maps_num: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    chunk_size: int = 1000
):
    start_dt = datetime.combine(date_from, time.min) if date_from else None
    end_dt = datetime.combine(date_to, time.max) if date_to else None

    result = await db.stream(
        SQL_FAST_MAPS_QUERY,
        {
            "maps_num": maps_num,
            "start_dt": start_dt,
            "end_dt": end_dt,
        }
    )

    async for partition in result.partitions(chunk_size):
        yield partition