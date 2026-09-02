"""Inspector & QC Critic Agent: Performs strict adversarial critique on architectural compliance, circulation paths, and ergonomic standards."""

from typing import Dict, Any, List
from autocad_ai.core.inspector import check_room_clear_dimensions, check_drafting_hygiene_overlaps, check_circulation_connectivity
from autocad_ai.core.standards import SPACE_STANDARDS


class InspectorCriticAgent:
    """Agent KTS_Inspector_QC: Chuyên gia Thẩm Định & Phản Biện Độc Lập ("Vạch lá tìm sâu")."""

    def __init__(self, name: str = "KTS_Inspector_QC"):
        self.name = name
        self.role = "Thẩm Định Độc Lập & Phản Biện Quy Chuẩn Kiến Trúc"

    def review_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Rà soát và phản biện gay gắt toàn diện phương án kiến trúc."""
        w_mm = proposal.get("building_width_mm", 12000.0)
        l_mm = proposal.get("building_length_mm", 12000.0)
        floors = proposal.get("floors", {})

        critiques = []
        passed_points = []
        score = 10.0

        for f_key, fl in floors.items():
            f_name = fl.get("name", f_key)
            rooms = fl.get("rooms", [])

            # 1. Rà soát liên thông giao thông (Circulation Pathfinding)
            conn_res = check_circulation_connectivity(rooms, w_mm, l_mm)
            if not conn_res["is_connected"]:
                score -= 3.0
                for err in conn_res["connectivity_issues"]:
                    critiques.append({
                        "floor": f_name,
                        "category": "circulation",
                        "severity": "CRITICAL",
                        "issue": err,
                        "suggested_fix": "Bắt buộc mở hành lang giao thông thông suốt rộng >= 1200mm bên cạnh cầu thang để kết nối tới phòng phía sau."
                    })
            else:
                passed_points.append(f"{f_name}: Giao thông liên thông thông suốt, không có phòng nào bị bít lối đi.")

            # 2. Rà soát kích thước thông thủy từng phòng (Neufert / QCVN 04)
            for r in rooms:
                r_name = r.get("name", "Phòng")
                rtype = r.get("type", "standard")
                rx1, rx2 = float(r.get("x1", 0)), float(r.get("x2", w_mm))
                ry1, ry2 = float(r.get("y1", 0)), float(r.get("y2", l_mm))
                rw = rx2 - rx1
                rl = ry2 - ry1

                dim_check = check_room_clear_dimensions(rl, rw, rtype)
                if not dim_check["is_standard_compliant"]:
                    score -= 1.0
                    for warn in dim_check["warnings"]:
                        critiques.append({
                            "floor": f_name,
                            "room": r_name,
                            "category": "ergonomics",
                            "severity": "WARNING",
                            "issue": warn,
                            "suggested_fix": f"Điều chỉnh kích thước phòng '{r_name}' đạt diện tích tối thiểu {dim_check['standard_min_area_m2']}m² và chiều rộng >= {dim_check['standard_min_width_mm']}mm."
                        })

            # 3. Rà soát chống chồng đè bản vẽ (Zero-Overlap)
            hygiene = check_drafting_hygiene_overlaps(rooms, w_mm, l_mm)
            if not hygiene["is_hygiene_clean"]:
                score -= 1.5
                for issue in hygiene["issues"]:
                    critiques.append({
                        "floor": f_name,
                        "category": "drafting_hygiene",
                        "severity": "WARNING",
                        "issue": issue,
                        "suggested_fix": "Duy trì khoảng hở an toàn >= 100mm giữa đồ nội thất và tường xây."
                    })
            else:
                passed_points.append(f"{f_name}: Đạt chuẩn vệ sinh bản vẽ Zero-Overlap (nội thất hở tường >= 100mm).")

        # Đánh giá chung
        score = max(0.0, min(10.0, score))
        is_approved = score >= 9.0 and not any(c.get("severity") == "CRITICAL" for c in critiques)

        return {
            "reviewer": self.name,
            "score": round(score, 1),
            "is_approved": is_approved,
            "verdict": "CHẤP THUẬN THÔNG QUA" if is_approved else "YÊU CẦU HIỆU CHỈNH LẠI",
            "critical_issues_count": len([c for c in critiques if c.get("severity") == "CRITICAL"]),
            "warnings_count": len([c for c in critiques if c.get("severity") == "WARNING"]),
            "critiques": critiques,
            "passed_points": passed_points,
        }
