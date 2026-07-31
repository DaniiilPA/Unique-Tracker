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
    onupdate=func.now()
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
    
    
SQL_FULL_ANALYTICS_QUERY = text("""
WITH filtered_maps AS (
    SELECT instance_id, area_name, updated_at, uniques
    FROM map_drops
    WHERE (CAST(:start_dt AS TIMESTAMP) IS NULL OR updated_at >= CAST(:start_dt AS TIMESTAMP))
      AND (CAST(:end_dt AS TIMESTAMP) IS NULL OR updated_at <= CAST(:end_dt AS TIMESTAMP))
    ORDER BY updated_at DESC
    LIMIT :maps_num
),
expanded_items AS (
    SELECT 
        fm.instance_id, fm.area_name, fm.updated_at, fm.uniques,
        kv.value->>1 AS item_name
    FROM filtered_maps fm
    LEFT JOIN LATERAL jsonb_each(fm.uniques) kv ON TRUE
),
map_aggregates AS (
    SELECT 
        fm.instance_id,
        fm.area_name,
        to_char(fm.updated_at, 'DD.MM.YYYY HH24:MI') as updated_at_str,
        (SELECT COUNT(*) FROM jsonb_object_keys(fm.uniques)) as total_uniques,
        COALESCE(
            (SELECT jsonb_object_agg(item_name, cnt) 
             FROM (
                 SELECT item_name, COUNT(*) as cnt 
                 FROM expanded_items ei 
                 WHERE ei.instance_id = fm.instance_id AND ei.item_name = ANY(:t0_items)
                 GROUP BY item_name
             ) t0_sub), '{}'::jsonb
        ) as t0_uniques,
        COALESCE(
            (SELECT jsonb_object_agg(item_name, cnt) 
             FROM (
                 SELECT item_name, COUNT(*) as cnt 
                 FROM expanded_items ei 
                 WHERE ei.instance_id = fm.instance_id AND ei.item_name = ANY(:t1_items)
                 GROUP BY item_name
             ) t1_sub), '{}'::jsonb
        ) as t1_uniques
    FROM filtered_maps fm
)
SELECT json_build_object(
    'grand_total', COALESCE((SELECT SUM(total_uniques) FROM map_aggregates), 0),
    't0_grand_total', COALESCE(
        (SELECT jsonb_object_agg(item_name, cnt) 
         FROM (SELECT item_name, COUNT(*) as cnt FROM expanded_items WHERE item_name = ANY(:t0_items) GROUP BY item_name) g0), '{}'::jsonb
    ),
    't1_grand_total', COALESCE(
        (SELECT jsonb_object_agg(item_name, cnt) 
         FROM (SELECT item_name, COUNT(*) as cnt FROM expanded_items WHERE item_name = ANY(:t1_items) GROUP BY item_name) g1), '{}'::jsonb
    ),
    'rows', COALESCE(
        (SELECT json_agg(json_build_object(
            'map_name', area_name,
            'updated_at', updated_at_str,
            'total_uniques', total_uniques,
            't0_uniques', t0_uniques,
            't1_uniques', t1_uniques
        )) FROM map_aggregates), '[]'::json
    )
) AS final_result;
""")

async def get_analytics_from_db(
    db: AsyncSession, 
    maps_num: int,
    t0_items: list[str] | set[str],
    t1_items: list[str] | set[str],
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> dict:
    start_dt = datetime.combine(date_from, time.min) if date_from else None
    end_dt = datetime.combine(date_to, time.max) if date_to else None

    result = await db.execute(
        SQL_FULL_ANALYTICS_QUERY,
        {
            "maps_num": maps_num,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "t0_items": list(t0_items),
            "t1_items": list(t1_items),
        }
    )
    return result.scalar_one()