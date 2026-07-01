"""FastAPI 主应用 - 原神角色档案 CRUD API (MySQL 版本)"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from database import get_db_connection
import math
import os

app = FastAPI(title="Genshin Character Archive API", version="2.0.0")

# 静态文件（角色图片等）
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Pydantic Schemas（数据校验）
# ============================================================
class CharacterCreate(BaseModel):
    character_name: str
    star_rarity: Optional[int] = None
    region: Optional[str] = None
    vision: Optional[str] = None
    weapon_type: Optional[str] = None
    model: Optional[str] = None
    constellation: Optional[str] = None
    birthday: Optional[str] = None
    special_dish: Optional[str] = None
    affiliation: Optional[str] = None
    limited: Optional[str] = None
    release_date: Optional[str] = None
    voice_en: Optional[str] = None
    voice_cn: Optional[str] = None
    voice_jp: Optional[str] = None
    voice_kr: Optional[str] = None


class CharacterUpdate(BaseModel):
    character_name: Optional[str] = None
    star_rarity: Optional[int] = None
    region: Optional[str] = None
    vision: Optional[str] = None
    weapon_type: Optional[str] = None
    model: Optional[str] = None
    constellation: Optional[str] = None
    birthday: Optional[str] = None
    special_dish: Optional[str] = None
    affiliation: Optional[str] = None
    limited: Optional[str] = None
    release_date: Optional[str] = None
    voice_en: Optional[str] = None
    voice_cn: Optional[str] = None
    voice_jp: Optional[str] = None
    voice_kr: Optional[str] = None


# ============================================================
# 辅助函数
# ============================================================
def get_growth_data(row: dict, stat_prefix: str) -> list:
    """从数据库行中提取角色成长数据（HP/ATK/DEF 在各级别的值）"""
    levels = [20, 40, 50, 60, 70, 80, 90]
    result = []
    for lv in levels:
        col = f"{stat_prefix}_{lv}_{lv}"
        result.append(int(row.get(col, 0) or 0))
    return result


# ============================================================
# CRUD 接口
# ============================================================

# ---------- READ：列表（分页+多条件筛选）----------
@app.get("/api/characters")
def list_characters(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=100),
    search: Optional[str] = None,
    region: Optional[str] = None,
    vision: Optional[str] = None,
    weapon_type: Optional[str] = None,
    star_rarity: Optional[int] = None,
):
    """角色列表：支持搜索 + 多维度筛选 + 分页"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []

            if search:
                conditions.append("character_name LIKE %s")
                params.append(f"%{search}%")
            if region:
                conditions.append("region = %s")
                params.append(region)
            if vision:
                conditions.append("vision = %s")
                params.append(vision)
            if weapon_type:
                conditions.append("weapon_type = %s")
                params.append(weapon_type)
            if star_rarity:
                conditions.append("star_rarity = %s")
                params.append(star_rarity)

            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            # 查总数
            cursor.execute(f"SELECT COUNT(*) AS total FROM characters {where}", params)
            total = cursor.fetchone()['total']

            # 分页查询
            offset = (page - 1) * page_size
            cursor.execute(
                f"""
                SELECT id, character_name, star_rarity, region, vision,
                       weapon_type, model, constellation, birthday, affiliation, limited
                FROM characters {where}
                ORDER BY star_rarity DESC, character_name ASC
                LIMIT %s OFFSET %s
                """,
                params + [page_size, offset]
            )
            rows = cursor.fetchall()

            return {
                "data": rows,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": math.ceil(total / page_size) if total > 0 else 0
            }
    finally:
        conn.close()


# ---------- READ：单个角色详情 ----------
@app.get("/api/characters/{character_id}")
def get_character(character_id: int):
    """角色完整详情：基础信息 + 成长曲线 + 同地区/同元素角色"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM characters WHERE id = %s", (character_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="角色不存在")

            data = dict(row)

            # 成长曲线数据
            data['hp_growth'] = get_growth_data(row, 'hp')
            data['atk_growth'] = get_growth_data(row, 'atk')
            data['def_growth'] = get_growth_data(row, 'def')

            # 同星级平均属性
            rarity = row.get('star_rarity', 5)
            cursor.execute(
                "SELECT * FROM characters WHERE star_rarity = %s AND id != %s",
                (rarity, character_id)
            )
            same_rarity = cursor.fetchall()

            levels = [20, 40, 50, 60, 70, 80, 90]
            for stat in ['hp', 'atk', 'def']:
                avg_list = []
                for lv in levels:
                    col = f"{stat}_{lv}_{lv}"
                    vals = [int(r.get(col, 0) or 0) for r in same_rarity]
                    avg_list.append(round(sum(vals) / len(vals)) if vals else 0)
                data[f'avg_{stat}_growth'] = avg_list

            # 同地区角色
            region = data.get('region')
            if region:
                cursor.execute(
                    "SELECT character_name FROM characters "
                    "WHERE region = %s AND id != %s LIMIT 8",
                    (region, character_id)
                )
                data['region_characters'] = [r['character_name'] for r in cursor.fetchall()]
            else:
                data['region_characters'] = []

            # 同元素角色
            vision = data.get('vision')
            if vision:
                cursor.execute(
                    "SELECT character_name FROM characters "
                    "WHERE vision = %s AND id != %s LIMIT 8",
                    (vision, character_id)
                )
                data['element_characters'] = [r['character_name'] for r in cursor.fetchall()]
            else:
                data['element_characters'] = []

            return data
    finally:
        conn.close()


# ---------- READ：按名字查角色（v2 URL 兼容 /character/:name）----------
@app.get("/api/characters/by-name/{name}")
def get_character_by_name(name: str):
    """按角色名获取完整详情（用于 Transition + Detail 页）"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM characters WHERE character_name = %s", (name,))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"角色 '{name}' 不存在")

            data = dict(row)
            data['hp_growth'] = get_growth_data(row, 'hp')
            data['atk_growth'] = get_growth_data(row, 'atk')
            data['def_growth'] = get_growth_data(row, 'def')

            rarity = row.get('star_rarity', 5)
            cid = row.get('id')
            cursor.execute(
                "SELECT * FROM characters WHERE star_rarity = %s AND id != %s", (rarity, cid)
            )
            same_rarity = cursor.fetchall()
            levels = [20, 40, 50, 60, 70, 80, 90]
            for stat in ['hp', 'atk', 'def']:
                avg_list = []
                for lv in levels:
                    col = f"{stat}_{lv}_{lv}"
                    vals = [int(r.get(col, 0) or 0) for r in same_rarity]
                    avg_list.append(round(sum(vals) / len(vals)) if vals else 0)
                data[f'avg_{stat}_growth'] = avg_list

            region = data.get('region')
            if region:
                cursor.execute(
                    "SELECT character_name FROM characters WHERE region = %s AND id != %s LIMIT 8",
                    (region, cid)
                )
                data['region_characters'] = [r['character_name'] for r in cursor.fetchall()]
            else:
                data['region_characters'] = []

            vision = data.get('vision')
            if vision:
                cursor.execute(
                    "SELECT character_name FROM characters WHERE vision = %s AND id != %s LIMIT 8",
                    (vision, cid)
                )
                data['element_characters'] = [r['character_name'] for r in cursor.fetchall()]
            else:
                data['element_characters'] = []

            return data
    finally:
        conn.close()


# ---------- 筛选选项 ----------
@app.get("/api/filters")
def get_filter_options():
    """获取筛选下拉框的选项值"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            filters = {}
            for col in ['region', 'vision', 'weapon_type']:
                cursor.execute(
                    f"SELECT DISTINCT {col} FROM characters "
                    f"WHERE {col} IS NOT NULL AND {col} != '' ORDER BY {col}"
                )
                filters[col] = [r[col] for r in cursor.fetchall()]

            cursor.execute(
                "SELECT DISTINCT star_rarity FROM characters ORDER BY star_rarity DESC"
            )
            filters['star_rarity'] = [r['star_rarity'] for r in cursor.fetchall()]

            return filters
    finally:
        conn.close()


# ---------- CREATE ----------
@app.post("/api/characters")
def create_character(char: CharacterCreate):
    """新增角色"""
    conn = get_db_connection()
    try:
        data = char.model_dump(exclude_none=True)
        if not data.get('character_name'):
            raise HTTPException(status_code=400, detail="角色名不能为空")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO characters ({columns}) VALUES ({placeholders})"

        with conn.cursor() as cursor:
            cursor.execute(sql, list(data.values()))
            conn.commit()
            new_id = cursor.lastrowid

        return {"message": "创建成功", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")
    finally:
        conn.close()


# ---------- UPDATE ----------
@app.put("/api/characters/{character_id}")
def update_character(character_id: int, char: CharacterUpdate):
    """修改角色信息"""
    conn = get_db_connection()
    try:
        data = char.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(status_code=400, detail="没有要更新的字段")

        set_parts = [f"{k} = %s" for k in data.keys()]
        sql = f"UPDATE characters SET {', '.join(set_parts)} WHERE id = %s"

        with conn.cursor() as cursor:
            cursor.execute(sql, list(data.values()) + [character_id])
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="角色不存在")

        return {"message": "更新成功", "id": character_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
    finally:
        conn.close()


# ---------- DELETE ----------
@app.delete("/api/characters/{character_id}")
def delete_character(character_id: int):
    """删除角色"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM characters WHERE id = %s", (character_id,))
            conn.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="角色不存在")

        return {"message": "删除成功", "id": character_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    finally:
        conn.close()


# ============================================================
# Dashboard 统计数据
# ============================================================

@app.get("/api/stats")
def get_stats():
    """Dashboard 统计图表数据"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            stats = {}

            cursor.execute(
                "SELECT vision AS name, COUNT(*) AS value FROM characters "
                "WHERE vision IS NOT NULL AND vision != '' "
                "GROUP BY vision ORDER BY value DESC"
            )
            stats['vision_distribution'] = cursor.fetchall()

            cursor.execute(
                "SELECT star_rarity AS name, COUNT(*) AS value FROM characters "
                "GROUP BY star_rarity ORDER BY name"
            )
            stats['rarity_distribution'] = cursor.fetchall()

            cursor.execute(
                "SELECT region AS name, COUNT(*) AS value FROM characters "
                "WHERE region IS NOT NULL AND region != '' "
                "GROUP BY region ORDER BY value DESC"
            )
            stats['region_distribution'] = cursor.fetchall()

            cursor.execute(
                "SELECT weapon_type AS name, COUNT(*) AS value FROM characters "
                "WHERE weapon_type IS NOT NULL AND weapon_type != '' "
                "GROUP BY weapon_type ORDER BY value DESC"
            )
            stats['weapon_distribution'] = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM characters")
            stats['total_characters'] = cursor.fetchone()['total']

            cursor.execute(
                "SELECT vision AS name, MAX(hp_90_90) AS value FROM characters "
                "WHERE vision IS NOT NULL AND vision != '' "
                "GROUP BY vision ORDER BY value DESC"
            )
            stats['max_hp_by_vision'] = cursor.fetchall()

            return stats
    finally:
        conn.close()


# ============================================================
# 地图坐标数据
# ============================================================

@app.get("/api/region-locations")
def get_region_locations():
    """获取地区坐标（Leaflet 地图标注用）"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT region, COUNT(*) AS cnt FROM characters "
                "WHERE region IS NOT NULL AND region != '' GROUP BY region"
            )
            rows = cursor.fetchall()

        # 提瓦特各地区 → 地球坐标映射（用于地图展示）
        region_coords = {
            'Mondstadt':   {'lat': 52.5, 'lng': 13.4,  'name_cn': '蒙德'},
            'Liyue':       {'lat': 39.9, 'lng': 116.4, 'name_cn': '璃月'},
            'Inazuma':     {'lat': 35.7, 'lng': 139.7, 'name_cn': '稻妻'},
            'Sumeru':      {'lat': 27.7, 'lng': 77.2,  'name_cn': '须弥'},
            'Fontaine':    {'lat': 48.9, 'lng': 2.3,   'name_cn': '枫丹'},
            'Natlan':      {'lat': 19.4, 'lng': -99.1, 'name_cn': '纳塔'},
            'Snezhnaya':   {'lat': 55.8, 'lng': 37.6,  'name_cn': '至冬'},
        }

        result = []
        for row in rows:
            region = row['region']
            coords = region_coords.get(region, {})
            result.append({
                'region': region,
                'name_cn': coords.get('name_cn', region),
                'lat': coords.get('lat', 0),
                'lng': coords.get('lng', 0),
                'character_count': row['cnt']
            })
        return result
    finally:
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
