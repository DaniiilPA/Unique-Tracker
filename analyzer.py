from datetime import date
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from depends import get_analytics_from_db
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

async def transform_db_records_to_analytics(
    db: AsyncSession,
    maps_num: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None
) -> FullAnalyticsResponse:

    raw_analytics = await get_analytics_from_db(
        db=db,
        maps_num=maps_num,
        t0_items=T0_ITEMS,
        t1_items=T1_ITEMS,
        date_from=date_from,
        date_to=date_to
    )
    return FullAnalyticsResponse.model_validate(raw_analytics)