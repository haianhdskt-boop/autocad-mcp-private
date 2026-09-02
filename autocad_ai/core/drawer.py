"""Drawer Engine: Generates DXF files for architectural floor plans."""

import ezdxf
from typing import Dict, Any, List
import math
import os

def draw_floor_plan_to_dxf(
    filepath: str,
    width_mm: float,
    length_mm: float,
    rooms: List[Dict[str, Any]],
    wall_ext_mm: float = 220.0,
    wall_int_mm: float = 110.0,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
    include_furniture: bool = True,
) -> str:
    """
    Generate an AutoCAD DXF file for a complete architectural floor plan.
    - filepath: Path to save the .dxf file
    - width_mm: House frontage width (X-axis)
    - length_mm: House depth/length (Y-axis)
    - rooms: List of room specs
    """
    doc = ezdxf.new('R2010', setup=True)
    doc.header['$INSUNITS'] = 4 # Millimeters
    msp = doc.modelspace()
    
    # 1. Setup Layers
    doc.layers.add("KT_TUONG_220", color=1)
    doc.layers.add("KT_TUONG_110", color=2)
    doc.layers.add("KT_CUA_DI", color=3)
    doc.layers.add("KT_CUA_SO", color=4)
    doc.layers.add("KT_THANG", color=5)
    doc.layers.add("KT_NOITHAT", color=8)
    doc.layers.add("KT_TEXT", color=7)
    doc.layers.add("KT_DIMS", color=9)
    
    # Text style for Unicode (ezdxf uses Arial by default which supports VN well)
    if "VnStyle" not in doc.styles:
        doc.styles.add("VnStyle", font="Arial.ttf")

    ox, oy = origin_x, origin_y
    w, l = width_mm, length_mm

    # 2. Outer boundary walls (220mm)
    p1 = [(ox, oy), (ox+w, oy), (ox+w, oy+l), (ox, oy+l)]
    msp.add_lwpolyline(p1, close=True, dxfattribs={'layer': 'KT_TUONG_220'})
    
    p2 = [(ox+wall_ext_mm, oy+wall_ext_mm), 
          (ox+w-wall_ext_mm, oy+wall_ext_mm), 
          (ox+w-wall_ext_mm, oy+l-wall_ext_mm), 
          (ox+wall_ext_mm, oy+l-wall_ext_mm)]
    msp.add_lwpolyline(p2, close=True, dxfattribs={'layer': 'KT_TUONG_220'})

    # 3. Interior rooms & dividing walls
    for r in rooms:
        r_name = r.get("name", "PHÒNG")
        y1 = oy + float(r.get("y_start", 0))
        y2 = oy + float(r.get("y_end", l))
        x1 = ox + float(r.get("x_start", wall_ext_mm))
        x2 = ox + float(r.get("x_end", w - wall_ext_mm))
        rtype = r.get("type", "standard").lower()

        # Draw horizontal dividing wall at y1 if not at bottom boundary
        if y1 > oy + wall_ext_mm and y1 < oy + l - wall_ext_mm:
            msp.add_line((x1, y1), (x2, y1), dxfattribs={'layer': 'KT_TUONG_110'})
            msp.add_line((x1, y1 + wall_int_mm), (x2, y1 + wall_int_mm), dxfattribs={'layer': 'KT_TUONG_110'})

        # Draw vertical dividing wall at x1 if not at left boundary
        if x1 > ox + wall_ext_mm and x1 < ox + w - wall_ext_mm:
            msp.add_line((x1, y1), (x1, y2), dxfattribs={'layer': 'KT_TUONG_110'})
            msp.add_line((x1 - wall_int_mm, y1), (x1 - wall_int_mm, y2), dxfattribs={'layer': 'KT_TUONG_110'})

        # Room label & area
        area_m2 = round(((x2 - x1) * (y2 - y1)) / 1_000_000.0, 1)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        text_y = y1 + 1000.0 if rtype in ("dining", "kitchen", "bep") else cy
        
        msp.add_text(
            f"{r_name}", 
            dxfattribs={'layer': 'KT_TEXT', 'height': 220, 'style': 'VnStyle'}
        ).set_placement((cx, text_y + 120), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        
        msp.add_text(
            f"(S = {area_m2}m2)", 
            dxfattribs={'layer': 'KT_TEXT', 'height': 160, 'style': 'VnStyle'}
        ).set_placement((cx, text_y - 180), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

        # Specific elements based on room type
        if rtype in ("stairs", "staircase", "thang"):
            stair_w = (x2 - x1)
            step_count = int(r.get("step_count", 10))
            step_depth = (y2 - y1) / max(step_count, 1)
            for s_idx in range(step_count + 1):
                sy = y1 + s_idx * step_depth
                msp.add_line((x1, sy), (x2, sy), dxfattribs={'layer': 'KT_THANG'})
            mid_x = cx
            msp.add_line((mid_x, y1), (mid_x, y2), dxfattribs={'layer': 'KT_THANG'})

        elif rtype in ("living", "khach") and include_furniture:
            p_sofa = [(x1+100, y1+400), (x1+950, y1+400), (x1+950, y2-400), (x1+100, y2-400)]
            msp.add_lwpolyline(p_sofa, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            p_table = [(x1+1250, cy-350), (x1+2050, cy-350), (x1+2050, cy+350), (x1+1250, cy+350)]
            msp.add_lwpolyline(p_table, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            p_tv = [(x2-450, y1+400), (x2-100, y1+400), (x2-100, y2-400), (x2-450, y2-400)]
            msp.add_lwpolyline(p_tv, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("dining", "kitchen", "bep") and include_furniture:
            table_cy = cy + 400.0
            p_table = [(cx-400, table_cy-500), (cx+400, table_cy-500), (cx+400, table_cy+500), (cx-400, table_cy+500)]
            msp.add_lwpolyline(p_table, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_line((x1+100, y2-600), (x2-100, y2-600), dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_line((x1+600, y1+100), (x1+600, y2-600), dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("wc", "bath", "ve_sinh") and include_furniture:
            msp.add_circle((x1+450, y1+450), radius=180, dxfattribs={'layer': 'KT_NOITHAT'})
            p_lavabo = [(x2-500, y2-400), (x2-100, y2-400), (x2-100, y2-100), (x2-500, y2-100)]
            msp.add_lwpolyline(p_lavabo, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

    doc.saveas(filepath)
    return filepath
