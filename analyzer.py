from collections import Counter
from datetime import date
import asyncio
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from depends import stream_raw_maps_from_db
from pydantic_schemas import FullAnalyticsResponse

T0_ITEMS = {"Bino's Kitchen Knife", "Bloodseeker", "Defiance of Destiny", "Divinarius", "Ephemeral Edge", "Essentia Sanguis", "Headhunter", "Jiquani's Potential", "Kalandra's Touch", "Lioneye's Glare",
            "Mageblood", "Marohi Erqi", "Rakiata's Dance", "Reefbane", "Soul Taker", "The Squire", "Varunastra", "Voltaxic Rift"
            }
T1_ITEMS = {"Abberath's Hooves", "Arakaali's Fang", "Dialla's Malefaction", "Eclipse Solaris", "Garukhan's Flight", "Gruthkul's Pelt", "Kitava's Feast", "Light of Lunaris", 
            "Martyr of Innocence", "Ralakesh's Impatience", "Aegis Aurora", "Akoya's Gaze", "Anathema", "Ancestral Vision", "Asenath's Mark", "Astral Projector", "Astramentis",
            "Ryslatha's Coil", "Shade of Solaris", "Sin's Rebirth", "The Brine Crown", "Tidebreaker", "Tukohama's Fortress", "Zerphi's Last Breath", "Death Rush", "Doedre's Skin",
            "Atziri's Foible", "Badge of the Brotherhood", "Binds of Bloody Vengeance", "Bloodnotch", "Cloak of Defiance", "Corpsewalker", "Cospri's Malice", "Darkscorn", "Dead Reckoning",
            "Doryani's Fist", "Doryani's Prototype", "Emperor's Vigilance", "Eyes of the Greatwolf", "Firesong", "Fleshcrafter", "Gravebind", "Hand of Heresy", "Heretic's Veil", "Hyrri's Ire",
            "Immutable Force", "Inpulsa's Broken Heart", "Inspired Learning", "Intuitive Leap", "Kaom's Heart", "Kaom's Primacy", "Kintsugi", "Lioneye's Fall", "Maata's Teaching", "Machina Mitts",
            "Maloney's Mechanism", "Might of the Meek", "Mjölner", "Prism Guardian", "Pure Talent", "Rathpith Globe", "Rigwald's Hunt", "Rigwald's Quills", "Seven-League Step", "Shavronne's Revelation",
            "Shavronne's Wrappings", "Skyforth", "Stormshroud", "Sunblast", "Stormshroud", "Taste of Hate", "The Brass Dome", "The Covenant", "The Fourth Vow", "The Gull", "The Iron Fortress", "The Magnate",
            "The Poet's Pen", "Thunderfist", "Unending Hunger", "Unnatural Instinct", "Utula's Hunger", "Void Battery", "Voll's Devotion", "Warrior's Legacy", "Windripper", "Witchbane", "Willclash"
            }

def _process_chunk(chunk_rows):
    chunk_grand_total = 0
    t0_grand = Counter()
    t1_grand = Counter()
    rows = []

    for _, area_name, updated_at_str, uniques in chunk_rows:
        if not uniques:
            uniques = {}

        total_map_uniques = len(uniques)
        chunk_grand_total += total_map_uniques

        t0_map = Counter()
        t1_map = Counter()

        for item_data in uniques.values():
            item_name = item_data[1] if isinstance(item_data, list) and len(item_data) > 1 else None
            
            if not item_name:
                continue

            if item_name in T0_ITEMS:
                t0_map[item_name] += 1
                t0_grand[item_name] += 1
            elif item_name in T1_ITEMS:
                t1_map[item_name] += 1
                t1_grand[item_name] += 1

        rows.append({
            "map_name": area_name,
            "updated_at": updated_at_str,
            "total_uniques": total_map_uniques,
            "t0_uniques": dict(t0_map),
            "t1_uniques": dict(t1_map)
        })

    return chunk_grand_total, t0_grand, t1_grand, rows


async def transform_db_records_to_analytics(
    db: AsyncSession,
    maps_num: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> FullAnalyticsResponse:
    grand_total = 0
    t0_grand_total = Counter()
    t1_grand_total = Counter()
    all_rows = []


    async for chunk in stream_raw_maps_from_db(db, maps_num, date_from, date_to, chunk_size=5):

        chunk_total, t0_chunk, t1_chunk, rows_chunk = await asyncio.to_thread(_process_chunk, chunk)


        grand_total += chunk_total
        t0_grand_total.update(t0_chunk)
        t1_grand_total.update(t1_chunk)
        all_rows.extend(rows_chunk)
        
        await asyncio.sleep(0)

    payload = {
        "grand_total": grand_total,
        "t0_grand_total": dict(t0_grand_total),
        "t1_grand_total": dict(t1_grand_total),
        "rows": all_rows
    }

    return FullAnalyticsResponse.model_validate(payload)