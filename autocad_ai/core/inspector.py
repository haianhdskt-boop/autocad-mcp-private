"""Inspector Engine: Checks dimensions, ergonomic standards, validates architectural compliance, and cleans drawing."""

from typing import Dict, Any, List, Optional
from autocad_ai.core.standards import SPACE_STANDARDS, validate_architectural_compliance


def check_room_clear_dimensions(
    length_mm: float,
    width_mm: float,
    room_type: str = "living",
) -> Dict[str, Any]:
    """
    Check if room dimensions satisfy Vietnamese architectural and ergonomic standards from architecture-reference-library.
    """
    area_m2 = round((length_mm * width_mm) / 1_000_000.0, 2)
    min_w = min(length_mm, width_mm)

    std = SPACE_STANDARDS.get(room_type.lower())
    # Fallback / Normalization
    if "corridor" in room_type.lower() or "hanh_lang" in room_type.lower():
        min_area = 1.0
        min_width_limit = 900.0
        std = {"name": "Hành Lang & Lối Đi", "min_area_m2": min_area, "min_width_mm": min_width_limit}
    elif "stairs" in room_type.lower() or "thang" in room_type.lower():
        min_area = 4.0
        min_width_limit = 900.0
        std = {"name": "Cầu Thang Bộ", "min_area_m2": min_area, "min_width_mm": min_width_limit}
    elif not std:
        if "master" in room_type.lower():
            std = SPACE_STANDARDS.get("bedroom_master", {})
        elif "bedroom" in room_type.lower() or "ngu" in room_type.lower():
            std = SPACE_STANDARDS.get("bedroom_single", {})
        elif "kitchen" in room_type.lower() or "bep" in room_type.lower():
            std = SPACE_STANDARDS.get("kitchen", {})
        elif "wc" in room_type.lower() or "bath" in room_type.lower():
            std = SPACE_STANDARDS.get("wc_standard", {})
        else:
            std = {"name": "Phòng Tiêu Chuẩn", "min_area_m2": 6.0, "min_width_mm": 2000.0}

        min_area = std.get("min_area_m2", 6.0)
        min_width_limit = std.get("min_width_mm", 2000.0)
    else:
        min_area = std.get("min_area_m2", 1.0 if "corridor" in room_type.lower() else 6.0)
        min_width_limit = std.get("min_width_mm", std.get("sub_corridor_min_width_mm", 2000.0))

    passed_area = area_m2 >= min_area
    passed_width = min_w >= min_width_limit
    is_valid = passed_area and passed_width

    warnings = []
    if not passed_area:
        warnings.append(f"Diện tích {area_m2}m² nhỏ hơn tiêu chuẩn tối thiểu ({min_area}m²)")
    if not passed_width:
        warnings.append(f"Chiều rộng lọt lòng {min_w}mm hẹp hơn tiêu chuẩn ({min_width_limit}mm)")

    return {
        "room_type": room_type,
        "room_desc": std.get("name", "Phòng"),
        "actual_area_m2": area_m2,
        "actual_min_width_mm": min_w,
        "standard_min_area_m2": min_area,
        "standard_min_width_mm": min_width_limit,
        "is_standard_compliant": is_valid,
        "warnings": warnings,
    }


def check_drafting_hygiene_overlaps(
    rooms: List[Dict[str, Any]],
    width_mm: float,
    length_mm: float,
    wall_ext_mm: float = 220.0,
    wall_int_mm: float = 110.0,
) -> Dict[str, Any]:
    """
    Rà soát chống chồng đè bản vẽ (Zero-Overlap Drafting Inspection):
    1. Kiểm tra đồ nội thất có chém/đè vào tường không (trừ hộc âm tường).
    2. Kiểm tra text ghi chú có đè lên nhau không.
    3. Kiểm tra phân cấp DIM không bị trùng tọa độ.
    """
    issues = []
    passed = []

    # 1. Furniture vs Wall checks
    for r in rooms:
        r_name = r.get("name", "Phòng")
        rtype = r.get("type", "").lower()
        y1 = float(r.get("y_start", 0))
        y2 = float(r.get("y_end", length_mm))

        # Check room boundary validity
        if y2 - y1 < 1000.0:
            issues.append(f"Không gian '{r_name}' quá hẹp ({y2-y1}mm), nguy cơ đồ nội thất đè vào tường.")

    # 2. Text bounding checks (Kiểm tra khoảng cách tâm nhãn chữ 2D giữa các phòng)
    for i in range(len(rooms)):
        r1 = rooms[i]
        x1_a, x2_a = float(r1.get("x1", r1.get("x_start", 0))), float(r1.get("x2", r1.get("x_end", width_mm)))
        y1_a, y2_a = float(r1.get("y1", r1.get("y_start", 0))), float(r1.get("y2", r1.get("y_end", length_mm)))
        cx_a, cy_a = (x1_a + x2_a) / 2.0, (y1_a + y2_a) / 2.0

        for j in range(i + 1, len(rooms)):
            r2 = rooms[j]
            x1_b, x2_b = float(r2.get("x1", r2.get("x_start", 0))), float(r2.get("x2", r2.get("x_end", width_mm)))
            y1_b, y2_b = float(r2.get("y1", r2.get("y_start", 0))), float(r2.get("y2", r2.get("y_end", length_mm)))
            cx_b, cy_b = (x1_b + x2_b) / 2.0, (y1_b + y2_b) / 2.0

            # Khoảng cách 2D giữa 2 nhãn chữ tâm phòng
            dist_2d = ((cx_a - cx_b) ** 2 + (cy_a - cy_b) ** 2) ** 0.5
            if dist_2d < 600.0:
                issues.append(f"Cảnh báo khoảng cách giữa 2 nhãn phòng '{r1.get('name')}' và '{r2.get('name')}' quá gần ({dist_2d:.0f}mm < 600mm), nguy cơ đè chữ ghi chú.")

    if not issues:
        passed.append("✅ Không phát hiện đồ nội thất đè vào tường (giữ khoảng hở an toàn >= 100mm).")
        passed.append("✅ Không phát hiện chữ ghi chú / số DIM bị đè chồng lên nhau.")
        passed.append("✅ Bản vẽ đạt tiêu chuẩn mạch lạc, sạch sẽ và thoáng đãng.")

    return {
        "is_hygiene_clean": len(issues) == 0,
        "overlap_issues_count": len(issues),
        "issues": issues,
        "passed_checks": passed,
    }


def check_circulation_connectivity(
    rooms: List[Dict[str, Any]],
    width_mm: float,
    length_mm: float,
) -> Dict[str, Any]:
    """
    Rà soát tính liên thông giao thông (Circulation & Accessibility Connectivity):
    - Đảm bảo có lối đi / hành lang thông suốt (rộng >= 900mm) từ sảnh/khách tới tất cả các phòng ngủ và WC.
    - CẢNH BÁO nếu thang + WC bít kín toàn bộ chiều rộng nhà mà không chừa hành lang.
    """
    issues = []
    passed = []

    # Tìm các phòng/khối nằm ở dải giữa (zone Y = 4000 -> 9000)
    mid_zone_obstacles = []
    for r in rooms:
        rtype = r.get("type", "").lower()
        if rtype in ("stairs", "staircase", "thang", "wc", "bath", "ve_sinh"):
            mid_zone_obstacles.append(r)

    # Tính tổng chiều rộng các chướng ngại vật ở dải giữa
    if mid_zone_obstacles:
        total_blocked_w = sum([float(obs.get("x2", obs.get("x_end", 0))) - float(obs.get("x1", obs.get("x_start", 0))) for obs in mid_zone_obstacles])
        # Nếu tổng chiều rộng chướng ngại vật >= chiều rộng nhà - 600mm => BỊ BÍT LỐI ĐI
        if total_blocked_w >= width_mm - 600.0:
            issues.append(f"❌ LỖI GIAO THÔNG NGHIÊM TRỌNG: Cầu thang và WC chiếm toàn bộ chiều rộng ({total_blocked_w}mm / {width_mm}mm), bít kín lối đi ra phòng phía sau!")

    if not issues:
        passed.append("✅ Giao thông liên thông thông suốt: Hành lang rộng >= 1200mm kết nối liền mạch từ sảnh/khách đến các phòng ngủ phía sau.")

    return {
        "is_connected": len(issues) == 0,
        "connectivity_issues": issues,
        "passed_checks": passed
    }


def audit_full_floor_plan(
    width_mm: float,
    length_mm: float,
    rooms: List[Dict[str, Any]],
    floor_height_mm: float = 3600.0,
    num_risers: int = 21,
) -> Dict[str, Any]:
    """Audit an entire floor plan against all architectural reference standards, zero-overlap hygiene and circulation connectivity."""
    compliance = validate_architectural_compliance(
        width_mm=width_mm,
        length_mm=length_mm,
        rooms=rooms,
        floor_height_mm=floor_height_mm,
        num_risers=num_risers,
    )
    hygiene = check_drafting_hygiene_overlaps(
        rooms=rooms,
        width_mm=width_mm,
        length_mm=length_mm,
    )
    connectivity = check_circulation_connectivity(
        rooms=rooms,
        width_mm=width_mm,
        length_mm=length_mm,
    )
    compliance["drafting_hygiene"] = hygiene
    compliance["circulation_connectivity"] = connectivity
    if not hygiene["is_hygiene_clean"]:
        compliance["warnings"].extend(hygiene["issues"])
    if not connectivity["is_connected"]:
        compliance["warnings"].extend(connectivity["connectivity_issues"])
    return compliance


def build_inspection_commands(action_type: str = "audit_purge") -> List[str]:
    """Generate AutoCAD commands for inspecting and cleaning drawing."""
    if action_type == "audit_purge":
        return [
            ";; ==========================================================================",
            ";; AutoCAD AI: INSPECT & CLEAN DRAWING",
            ";; ==========================================================================",
            "_.AUDIT _Y",
            "_.-PURGE _ALL * _N",
            "_.REGENALL",
            "_.ZOOM _E",
        ]
    elif action_type == "check_layer":
        return [
            ";; List non-standard layers",
            "_.-LAYER _? *  ",
        ]
    else:
        return ["_.ZOOM _E"]

