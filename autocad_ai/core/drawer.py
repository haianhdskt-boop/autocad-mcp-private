"""Drawer Engine: Generates professional DXF architectural floor plans."""

import ezdxf
from typing import Dict, Any, List, Optional
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
    title: str = "MẶT BẰNG TẦNG 1 - BIỆT THỰ SINH THÁI",
    scale_text: str = "TỶ LỆ: 1/100",
    pool_rect: Optional[Dict[str, float]] = None,
) -> str:
    """
    Generate an AutoCAD DXF file for a complete architectural floor plan.
    - filepath: Path to save the .dxf file
    - width_mm: House frontage width (X-axis)
    - length_mm: House depth/length (Y-axis)
    - rooms: List of room specs
    - pool_rect: Optional dict with x, y, width, length for swimming pool
    """
    doc = ezdxf.new('R2010', setup=True)
    doc.header['$INSUNITS'] = 4  # Millimeters
    msp = doc.modelspace()
    
    # 1. Setup Standard Architectural Layers
    layers_config = [
        ("KT_TUONG_220", 1),  # Red
        ("KT_TUONG_110", 2),  # Yellow
        ("KT_COT", 6),        # Magenta
        ("KT_CUA_DI", 3),     # Green
        ("KT_CUA_SO", 4),     # Cyan
        ("KT_THANG", 5),      # Blue
        ("KT_NOITHAT", 8),    # Dark Grey
        ("KT_TEXT", 7),       # White/Black
        ("KT_DIMS", 9),       # Light Grey
        ("KT_TRUC", 1),       # Red (Centerlines)
        ("KT_CANH_QUAN", 3),  # Green (Pool / Garden)
    ]
    for name, color in layers_config:
        if name not in doc.layers:
            doc.layers.add(name, color=color)
    
    # Text style for Unicode
    if "VnStyle" not in doc.styles:
        doc.styles.add("VnStyle", font="Arial.ttf")

    ox, oy = origin_x, origin_y
    w, l = width_mm, length_mm

    # 2. Outer Boundary Walls (220mm)
    p_outer = [(ox, oy), (ox + w, oy), (ox + w, oy + l), (ox, oy + l)]
    msp.add_lwpolyline(p_outer, close=True, dxfattribs={'layer': 'KT_TUONG_220'})
    
    p_inner = [
        (ox + wall_ext_mm, oy + wall_ext_mm), 
        (ox + w - wall_ext_mm, oy + wall_ext_mm), 
        (ox + w - wall_ext_mm, oy + l - wall_ext_mm), 
        (ox + wall_ext_mm, oy + l - wall_ext_mm)
    ]
    msp.add_lwpolyline(p_inner, close=True, dxfattribs={'layer': 'KT_TUONG_220'})

    # 3. Columns at corners & grid (220x220mm)
    col_coords = [
        (ox, oy), (ox + w/2 - 110, oy), (ox + w - 220, oy),
        (ox, oy + l/2 - 110), (ox + w - 220, oy + l/2 - 110),
        (ox, oy + l - 220), (ox + w/2 - 110, oy + l - 220), (ox + w - 220, oy + l - 220),
    ]
    for cx, cy in col_coords:
        p_col = [(cx, cy), (cx + 220, cy), (cx + 220, cy + 220), (cx, cy + 220)]
        msp.add_lwpolyline(p_col, close=True, dxfattribs={'layer': 'KT_COT'})
        # Column hatch cross
        msp.add_line((cx, cy), (cx + 220, cy + 220), dxfattribs={'layer': 'KT_COT'})
        msp.add_line((cx + 220, cy), (cx, cy + 220), dxfattribs={'layer': 'KT_COT'})

    # 4. Interior Rooms & Partition Walls
    for r in rooms:
        r_name = r.get("name", "PHÒNG")
        y1 = oy + float(r.get("y_start", 0))
        y2 = oy + float(r.get("y_end", l))
        x1 = ox + float(r.get("x_start", wall_ext_mm))
        x2 = ox + float(r.get("x_end", w - wall_ext_mm))
        rtype = r.get("type", "standard").lower()

        # Horizontal partition wall at y1
        if y1 > oy + wall_ext_mm and y1 < oy + l - wall_ext_mm:
            msp.add_line((x1, y1), (x2, y1), dxfattribs={'layer': 'KT_TUONG_110'})
            msp.add_line((x1, y1 + wall_int_mm), (x2, y1 + wall_int_mm), dxfattribs={'layer': 'KT_TUONG_110'})

        # Vertical partition wall at x1
        if x1 > ox + wall_ext_mm and x1 < ox + w - wall_ext_mm:
            msp.add_line((x1, y1), (x1, y2), dxfattribs={'layer': 'KT_TUONG_110'})
            msp.add_line((x1 - wall_int_mm, y1), (x1 - wall_int_mm, y2), dxfattribs={'layer': 'KT_TUONG_110'})

        # Room Label & Area Calculation
        room_w = x2 - x1
        room_l = y2 - y1
        area_m2 = round((room_w * room_l) / 1_000_000.0, 1)
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0

        text_y = y1 + 1200.0 if rtype in ("dining", "kitchen", "bep") else (y1 + 800.0 if rtype in ("living", "khach") else cy)
        
        msp.add_text(
            f"{r_name.upper()}", 
            dxfattribs={'layer': 'KT_TEXT', 'height': 200, 'style': 'VnStyle'}
        ).set_placement((cx, text_y + 110), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        
        msp.add_text(
            f"S = {area_m2} m²", 
            dxfattribs={'layer': 'KT_TEXT', 'height': 150, 'style': 'VnStyle'}
        ).set_placement((cx, text_y - 140), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

        # 5. Room Interior & Architectural Details (Strict Non-overlapping)
        if rtype in ("stairs", "staircase", "thang"):
            stair_w = room_w
            flight_w = (stair_w - 200) / 2.0
            step_count = int(r.get("step_count", 10))
            step_depth = (room_l) / max(step_count, 1)
            
            # Flight 1 (Left, going UP)
            for s_idx in range(step_count + 1):
                sy = y1 + s_idx * step_depth
                msp.add_line((x1, sy), (x1 + flight_w, sy), dxfattribs={'layer': 'KT_THANG'})
            # Flight 2 (Right, going DOWN)
            for s_idx in range(step_count + 1):
                sy = y1 + s_idx * step_depth
                msp.add_line((x2 - flight_w, sy), (x2, sy), dxfattribs={'layer': 'KT_THANG'})
            # Mid void (Khe thang 200mm)
            msp.add_line((x1 + flight_w, y1), (x1 + flight_w, y2), dxfattribs={'layer': 'KT_THANG'})
            msp.add_line((x2 - flight_w, y1), (x2 - flight_w, y2), dxfattribs={'layer': 'KT_THANG'})
            # Up arrow
            arrow_x = x1 + flight_w / 2.0
            msp.add_line((arrow_x, y1 + 300), (arrow_x, y2 - 300), dxfattribs={'layer': 'KT_THANG'})
            msp.add_line((arrow_x, y2 - 300), (arrow_x - 120, y2 - 600), dxfattribs={'layer': 'KT_THANG'})
            msp.add_line((arrow_x, y2 - 300), (arrow_x + 120, y2 - 600), dxfattribs={'layer': 'KT_THANG'})
            msp.add_text("UP (LÊN TẦNG 2)", dxfattribs={'layer': 'KT_TEXT', 'height': 130, 'style': 'VnStyle'}).set_placement((arrow_x, cy), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

        elif rtype in ("living", "khach") and include_furniture:
            # Sofa L-shape (Clear from wall >= 150mm)
            p_sofa_main = [(x1 + 200, y1 + 800), (x1 + 1100, y1 + 800), (x1 + 1100, y2 - 800), (x1 + 200, y2 - 800)]
            p_sofa_arm = [(x1 + 1100, y2 - 1800), (x1 + 2800, y2 - 1800), (x1 + 2800, y2 - 900), (x1 + 1100, y2 - 900)]
            msp.add_lwpolyline(p_sofa_main, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_lwpolyline(p_sofa_arm, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            
            # Coffee table
            p_table = [(cx - 600, cy - 400), (cx + 600, cy - 400), (cx + 600, cy + 400), (cx - 600, cy + 400)]
            msp.add_lwpolyline(p_table, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            
            # TV Cabinet
            p_tv = [(x2 - 500, y1 + 800), (x2 - 150, y1 + 800), (x2 - 150, y2 - 800), (x2 - 500, y2 - 800)]
            msp.add_lwpolyline(p_tv, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("tra_dao", "tea", "tea_room") and include_furniture:
            # Low tea table & floor cushions
            p_tea = [(cx - 700, cy - 350), (cx + 700, cy - 350), (cx + 700, cy + 350), (cx - 700, cy + 350)]
            msp.add_lwpolyline(p_tea, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            # 4 cushions
            for dx, dy in [(-900, 0), (900, 0), (0, -550), (0, 550)]:
                c_poly = [(cx + dx - 200, cy + dy - 200), (cx + dx + 200, cy + dy - 200), 
                          (cx + dx + 200, cy + dy + 200), (cx + dx - 200, cy + dy + 200)]
                msp.add_lwpolyline(c_poly, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("dining", "kitchen", "bep") and include_furniture:
            # 8-person Dining Table (Centered)
            table_cy = cy + 400.0
            p_dining = [(cx - 1000, table_cy - 450), (cx + 1000, table_cy - 450), 
                        (cx + 1000, table_cy + 450), (cx - 1000, table_cy + 450)]
            msp.add_lwpolyline(p_dining, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            
            # Dining chairs
            for i in range(4):
                chair_x = (cx - 750) + i * 500
                p_c1 = [(chair_x - 180, table_cy - 700), (chair_x + 180, table_cy - 700),
                        (chair_x + 180, table_cy - 500), (chair_x - 180, table_cy - 500)]
                p_c2 = [(chair_x - 180, table_cy + 500), (chair_x + 180, table_cy + 500),
                        (chair_x + 180, table_cy + 700), (chair_x - 180, table_cy + 700)]
                msp.add_lwpolyline(p_c1, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
                msp.add_lwpolyline(p_c2, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
                
            # L-shaped Kitchen Counter
            msp.add_line((x1 + 150, y2 - 650), (x2 - 150, y2 - 650), dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_line((x1 + 650, y1 + 150), (x1 + 650, y2 - 650), dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("bed", "bedroom", "ngu") and include_furniture:
            # Master / Elder Bed (1800x2000mm)
            bed_w, bed_l = 1800.0, 2000.0
            p_bed = [(cx - bed_w/2, y2 - bed_l - 150), (cx + bed_w/2, y2 - bed_l - 150),
                     (cx + bed_w/2, y2 - 150), (cx - bed_w/2, y2 - 150)]
            msp.add_lwpolyline(p_bed, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            # Pillows
            p_pil1 = [(cx - 700, y2 - 550), (cx - 150, y2 - 550), (cx - 150, y2 - 250), (cx - 700, y2 - 250)]
            p_pil2 = [(cx + 150, y2 - 550), (cx + 700, y2 - 550), (cx + 700, y2 - 250), (cx + 150, y2 - 250)]
            msp.add_lwpolyline(p_pil1, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_lwpolyline(p_pil2, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            # Nightstands
            p_ns1 = [(cx - bed_w/2 - 500, y2 - 600), (cx - bed_w/2 - 100, y2 - 600),
                     (cx - bed_w/2 - 100, y2 - 150), (cx - bed_w/2 - 500, y2 - 150)]
            p_ns2 = [(cx + bed_w/2 + 100, y2 - 600), (cx + bed_w/2 + 500, y2 - 600),
                     (cx + bed_w/2 + 500, y2 - 150), (cx + bed_w/2 + 100, y2 - 150)]
            msp.add_lwpolyline(p_ns1, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            msp.add_lwpolyline(p_ns2, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            # Wardrobe
            p_ward = [(x1 + 150, y1 + 200), (x1 + 650, y1 + 200), (x1 + 650, y2 - 800), (x1 + 150, y2 - 800)]
            msp.add_lwpolyline(p_ward, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

        elif rtype in ("wc", "bath", "ve_sinh") and include_furniture:
            # Toilet bowl (hở tường 150mm)
            msp.add_circle((x1 + 500, y1 + 500), radius=200, dxfattribs={'layer': 'KT_NOITHAT'})
            # Lavabo (offset 100mm)
            p_lavabo = [(x2 - 600, y2 - 450), (x2 - 150, y2 - 450), (x2 - 150, y2 - 150), (x2 - 600, y2 - 150)]
            msp.add_lwpolyline(p_lavabo, close=True, dxfattribs={'layer': 'KT_NOITHAT'})
            # Glass partition / Shower booth (900x900mm)
            p_shower = [(x1 + 150, y2 - 950), (x1 + 950, y2 - 950), (x1 + 950, y2 - 150), (x1 + 150, y2 - 150)]
            msp.add_lwpolyline(p_shower, close=True, dxfattribs={'layer': 'KT_NOITHAT'})

    # 6. Exterior Swimming Pool (If specified)
    if pool_rect:
        px = pool_rect.get("x", ox + w + 1500)
        py = pool_rect.get("y", oy + 1000)
        pw = pool_rect.get("width", 4000)
        pl = pool_rect.get("length", 10000)
        
        # Pool water body
        p_pool = [(px, py), (px + pw, py), (px + pw, py + pl), (px, py + pl)]
        msp.add_lwpolyline(p_pool, close=True, dxfattribs={'layer': 'KT_CANH_QUAN'})
        
        # Pool deck (Sàn gỗ ngoài trời 1000mm)
        p_deck = [(px - 800, py - 800), (px + pw + 800, py - 800), (px + pw + 800, py + pl + 800), (px - 800, py + pl + 800)]
        msp.add_lwpolyline(p_deck, close=True, dxfattribs={'layer': 'KT_CANH_QUAN'})
        
        msp.add_text("BỂ BƠI NGOÀI TRỜI (4.0 x 10.0m)", dxfattribs={'layer': 'KT_TEXT', 'height': 220, 'style': 'VnStyle'}).set_placement((px + pw/2, py + pl/2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        msp.add_text("S = 40.0 m² (Độ sâu 1.2m - 1.6m)", dxfattribs={'layer': 'KT_TEXT', 'height': 150, 'style': 'VnStyle'}).set_placement((px + pw/2, py + pl/2 - 350), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)

    # 7. Dimensions & Grid System
    # Overall Dimension X (Bottom)
    dim_y = oy - 1500
    msp.add_line((ox, dim_y), (ox + w, dim_y), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_line((ox, oy), (ox, dim_y - 200), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_line((ox + w, oy), (ox + w, dim_y - 200), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_text(f"{int(w)}", dxfattribs={'layer': 'KT_DIMS', 'height': 250, 'style': 'VnStyle'}).set_placement((ox + w/2, dim_y + 100), align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)

    # Overall Dimension Y (Left)
    dim_x = ox - 1500
    msp.add_line((dim_x, oy), (dim_x, oy + l), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_line((ox, oy), (dim_x - 200, oy), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_line((ox, oy + l), (dim_x - 200, oy + l), dxfattribs={'layer': 'KT_DIMS'})
    msp.add_text(f"{int(l)}", dxfattribs={'layer': 'KT_DIMS', 'height': 250, 'style': 'VnStyle'}).set_placement((dim_x - 100, oy + l/2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_RIGHT)

    # 8. Drawing Title & Metadata Block
    title_y = oy - 2800
    msp.add_text(title, dxfattribs={'layer': 'KT_TEXT', 'height': 400, 'style': 'VnStyle'}).set_placement((ox + w/2, title_y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(scale_text, dxfattribs={'layer': 'KT_TEXT', 'height': 200, 'style': 'VnStyle'}).set_placement((ox + w/2, title_y - 500), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((ox + w/2 - 2500, title_y - 220), (ox + w/2 + 2500, title_y - 220), dxfattribs={'layer': 'KT_TEXT'})

    # Save to file
    doc.saveas(filepath)
    return filepath
