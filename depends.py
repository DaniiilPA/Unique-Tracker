import datetime
from typing import AsyncGenerator
from sqlalchemy import BigInteger, DateTime, func, select, desc
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
    
    updated_at: Mapped[datetime.datetime] = mapped_column(
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
    
    
async def get_all_uniques(db: AsyncSession, maps_num: int):
    
    stmt = (
        select(MapDrop)
        .where(MapDrop.area_name.in_(ALLOWED_AREAS))
        .order_by(desc(MapDrop.updated_at))
        .limit(maps_num)
    )
    
    result = await db.execute(stmt)
    
    return result.scalars().all()