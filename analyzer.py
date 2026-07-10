from pydantic_schemas import MapAnalyticsRow, FullAnalyticsResponse
from depends import MapDrop
T0_ITEMS = ["Bino's Kitchen Knife", "Bloodseeker", "Defiance of Destiny", "Divinarius", "T0Ephemeral Edge", "Essentia Sanguis", "Headhunter", "Jiquani's Potential", "Kalandra's Touch", "Lioneye's Glare",
            "Mageblood", "Marohi Erqi", "Rakiata's Dance", "Reefbane", "Soul Taker", "The Squire", "Varunastra", "Voltaxic Rift"
            ]
T1_ITEMS = ["Abberath's Hooves", "Arakaali's Fang", "Dialla's Malefaction", "Eclipse Solaris", "Garukhan's Flight", "Gruthkul's Pelt", "Kitava's Feast", "Light of Lunaris", 
            "Martyr of Innocence", "Ralakesh's Impatience", "Aegis Aurora", "Akoya's Gaze", "Anathema", "Ancestral Vision", "Asenath's Mark", "Astral Projector", "Astramentis",
            "Ryslatha's Coil", "Shade of Solaris", "Sin's Rebirth", "The Brine Crown", "Tidebreaker", "Tukohama's Fortress", "Zerphi's Last Breath", "Death Rush", "Doedre's Skin",
            "Atziri's Foible", "Badge of the Brotherhood", "Binds of Bloody Vengeance", "Bloodnotch", "Cloak of Defiance", "Corpsewalker", "Cospri's Malice", "Darkscorn", "Dead Reckoning",
            "Doryani's Fist", "Doryani's Prototype", "Emperor's Vigilance", "Eyes of the Greatwolf", "Firesong", "Fleshcrafter", "Gravebind", "Hand of Heresy", "Heretic's Veil", "Hyrri's Ire",
            "Immutable Force", "Inpulsa's Broken Heart", "Inspired Learning", "Intuitive Leap", "Kaom's Heart", "Kaom's Primacy", "Kintsugi", "Lioneye's Fall", "Maata's Teaching", "Machina Mitts",
            "Maloney's Mechanism", "Might of the Meek", "Mjölner", "Prism Guardian", "Pure Talent", "Rathpith Globe", "Rigwald's Hunt", "Rigwald's Quills", "Seven-League Step", "Shavronne's Revelation",
            "Shavronne's Wrappings", "Skyforth", "Stormshroud", "Sunblast", "Stormshroud", "Taste of Hate", "The Brass Dome", "The Covenant", "The Fourth Vow", "The Gull", "The Iron Fortress", "The Magnate",
            "The Poet's Pen", "Thunderfist", "Unending Hunger", "Unnatural Instinct", "Utula's Hunger", "Void Battery", "Voll's Devotion", "Warrior's Legacy", "Windripper", "Witchbane"
            ]

def transform_db_records_to_analytics(records: list[MapDrop]) -> FullAnalyticsResponse:
    analytics_rows = []
    grand_total = 0
    t0_total_grand = {}
    t1_total_grand = {}
    
    for record in records:
        uniques_dict: dict = record.uniques
        
        t0 = {}
        t1 = {}
        total_count = len(uniques_dict)
        
        for item_id, item_info in uniques_dict.items():
            item_name = item_info[1]
            
            if item_name in T0_ITEMS:
                t0[item_name] = t0.get(item_name, 0) + 1
                t0_total_grand[item_name] = t0_total_grand.get(item_name, 0) + 1
            elif item_name in T1_ITEMS:
                t1_total_grand[item_name] = t1_total_grand.get(item_name, 0) + 1
                
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
        
    return FullAnalyticsResponse(grand_total=grand_total, t0_uniques=t0_total_grand, t1_uniques=t1_total_grand, rows=analytics_rows)