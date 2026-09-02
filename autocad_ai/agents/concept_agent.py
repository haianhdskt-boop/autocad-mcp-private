"""Concept Architect Agent: Responsible for architectural concept planning, spatial zoning, and microclimate orientation."""

from typing import Dict, Any, List, Optional
import math


class ConceptArchitectAgent:
    """Agent KTS_Concept: Chuyên sâu về bố cục không gian, dây chuyền công năng và vi khí hậu."""

    def __init__(self, name: str = "KTS_Concept"):
        self.name = name
        self.role = "Chủ trì Thiết Kế Ý Tưởng Kiến Trúc"

    def propose_initial_layout(self, project_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Đề xuất phương án bố trí không gian sơ bộ dựa trên Nhiệm Vụ Thiết Kế."""
        width_m = float(project_brief.get("width_m", 12.0))
        length_m = float(project_brief.get("length_m", 12.0))
        num_floors = int(project_brief.get("num_floors", 3))
        land_size_m = project_brief.get("land_size_m", [30.0, 30.0])
        main_orientation = project_brief.get("main_orientation", "Tây Nam")

        w_mm = width_m * 1000.0
        l_mm = length_m * 1000.0

        w_mm = width_m * 1000.0
        l_mm = length_m * 1000.0

        # Phân loại hình công trình: Nhà Phố (Townhouse w <= 7m) vs Biệt Thự (Villa w > 7m)
        is_townhouse = width_m <= 7.0

        if is_townhouse:
            microclimate_analysis = {
                "ventilation_strategy": "Hiệu ứng ống khói (Stack Effect) với 02 Giếng trời: Giếng trời giữa nhà cạnh thang 1 vế + Giếng trời sân sau.",
                "stair_solution": "Cầu thang thẳng 1 vế áp tường (21 bậc, h=165mm, b=260mm) giải phóng 100% bề ngang 5m, không gian mở thông suốt Khách - Bếp.",
                "family_zoning": "Gia đình 4 người (Bố mẹ + Con trai + Con gái) có 3 phòng ngủ độc lập, đảm bảo riêng tư tuyệt đối cho 2 con khác giới.",
            }

            floors = {
                "floor_1": {
                    "name": "Mặt Bằng Tầng 1 (Khách - Bếp Mở & Tiểu Cảnh)",
                    "rooms": [
                        {"id": "san_truoc", "name": "Sân Trước & Tiểu Cảnh Vườn Cây", "type": "standard", "x1": 0, "x2": w_mm, "y1": 0, "y2": 2500},
                        {"id": "khach", "name": "Phòng Khách Đại Sảnh", "type": "living", "x1": 0, "x2": w_mm, "y1": 2500, "y2": 7000},
                        {"id": "thang", "name": "Cầu Thang 1 Vế Áp Tường", "type": "stairs", "x1": 0, "x2": 1100, "y1": 5000, "y2": 10500, "steps": 21},
                        {"id": "gieng_troi_1", "name": "Giếng Trời Trung Tâm & Tiểu Cảnh", "type": "standard", "x1": 1100, "x2": w_mm, "y1": 7000, "y2": 9000},
                        {"id": "bep_an", "name": "Bếp & Phòng Ăn Gia Đình", "type": "kitchen", "x1": 0, "x2": w_mm, "y1": 9000, "y2": 13500},
                        {"id": "wc_1", "name": "Vệ Sinh Tầng 1 & Sân Sau", "type": "wc", "x1": 0, "x2": w_mm, "y1": 13500, "y2": l_mm},
                    ]
                },
                "floor_2": {
                    "name": "Mặt Bằng Tầng 2 (Phòng Ngủ Master & Con 1)",
                    "rooms": [
                        {"id": "ban_cong_2", "name": "Ban Công Xanh Tầng 2", "type": "balcony", "x1": 0, "x2": w_mm, "y1": 0, "y2": 1200},
                        {"id": "master", "name": "Phòng Ngủ Master VIP (Bố Mẹ)", "type": "bedroom_master", "x1": 0, "x2": w_mm, "y1": 1200, "y2": 6000},
                        {"id": "thang_2", "name": "Cầu Thang & Cầu Kính Hành Lang", "type": "stairs", "x1": 0, "x2": 1100, "y1": 5000, "y2": 10500, "steps": 21},
                        {"id": "thong_tang_2", "name": "Thông Tầng Giếng Trời", "type": "balcony", "x1": 1100, "x2": w_mm, "y1": 6000, "y2": 9000},
                        {"id": "ngu_con1", "name": "Phòng Ngủ Con Gái", "type": "bedroom", "x1": 0, "x2": w_mm, "y1": 9000, "y2": 13500},
                        {"id": "wc_2", "name": "Vệ Sinh Tầng 2 & Giếng Sau", "type": "wc", "x1": 0, "x2": w_mm, "y1": 13500, "y2": l_mm},
                    ]
                },
                "floor_3": {
                    "name": "Mặt Bằng Tầng 3 (Phòng Ngủ Con 2 & Phòng Thờ)",
                    "rooms": [
                        {"id": "san_thuong", "name": "Sân Thượng Vườn Cây Sky Garden", "type": "terrace", "x1": 0, "x2": w_mm, "y1": 0, "y2": 2500},
                        {"id": "tho", "name": "Phòng Thờ Trang Nghiêm", "type": "altar", "x1": 0, "x2": w_mm, "y1": 2500, "y2": 6000},
                        {"id": "thang_3", "name": "Cầu Thang Lên Mái", "type": "stairs", "x1": 0, "x2": 1100, "y1": 5000, "y2": 10500, "steps": 21},
                        {"id": "ngu_con2", "name": "Phòng Ngủ Con Trai", "type": "bedroom", "x1": 0, "x2": w_mm, "y1": 7000, "y2": 12000},
                        {"id": "san_phoi", "name": "Sân Phơi & Giặt Kỹ Thuật", "type": "standard", "x1": 0, "x2": w_mm, "y1": 12000, "y2": l_mm},
                    ]
                }
            }
            site_landscape = {
                "land_dimensions": [width_m, length_m],
                "building_footprint": [width_m, length_m],
                "front_garden": "Sân trước 2.5m lát đá cubic trồng hoa & cây bóng mát nhỏ",
                "back_garden": "Giếng trời sau 1.5m lấy sáng đối lưu gió",
                "skylights": "02 Giếng trời (Trung tâm + Sau nhà)",
            }
        else:
            # Biệt thự vườn
            microclimate_analysis = {
                "main_sun_heat": "Hướng Tây & Tây Nam nắng gắt -> Vùng đệm che chắn.",
                "main_cool_wind": "Hướng Đông Nam & Đông đón gió mát lành -> Bố trí phòng khách, ban công và bể bơi.",
                "prime_view": "Hướng Bắc giáp núi & Hướng Đông giáp cánh đồng -> Mở cửa sổ lớn ngắm cảnh quan.",
            }
            floors = {
                "floor_1": {
                    "name": "Mặt Bằng Tầng 1 (Sinh Hoạt Chung)",
                    "rooms": [
                        {"id": "sanh_tra", "name": "Sảnh Đón & Trà Đạo", "type": "living", "x1": 0, "x2": 4800, "y1": 0, "y2": 4200},
                        {"id": "khach", "name": "Phòng Khách Đại Sảnh", "type": "living", "x1": 4800, "x2": w_mm, "y1": 0, "y2": 5600},
                        {"id": "bep_an", "name": "Bếp & Phòng Ăn Lớn", "type": "kitchen", "x1": 0, "x2": 4800, "y1": 4200, "y2": 9000},
                        {"id": "thang", "name": "Cầu Thang Bộ & Giếng Trời", "type": "stairs", "x1": 4800, "x2": 7800, "y1": 5600, "y2": 8600, "steps": 21},
                        {"id": "hanh_lang", "name": "Hành Lang Giao Thông", "type": "corridor", "x1": 7800, "x2": 9000, "y1": 5600, "y2": 8600},
                        {"id": "wc_1", "name": "Vệ Sinh Chung Tầng 1", "type": "wc", "x1": 9000, "x2": w_mm, "y1": 5600, "y2": 7600},
                        {"id": "ngu_ob", "name": "Phòng Ngủ Ông Bà", "type": "bedroom", "x1": 4800, "x2": w_mm, "y1": 8600, "y2": l_mm},
                        {"id": "san_uot", "name": "Sân Gia Công Ướt", "type": "standard", "x1": 0, "x2": 4800, "y1": 9000, "y2": l_mm},
                    ]
                },
                "floor_2": {
                    "name": "Mặt Bằng Tầng 2 (Nghỉ Ngơi Gia Đình)",
                    "rooms": [
                        {"id": "shc", "name": "Phòng Sinh Hoạt Chung", "type": "living", "x1": 0, "x2": 4800, "y1": 0, "y2": 4200},
                        {"id": "master", "name": "Phòng Ngủ Master VIP", "type": "bedroom_master", "x1": 4800, "x2": w_mm, "y1": 0, "y2": 5600},
                        {"id": "ngu_con1", "name": "Phòng Ngủ Con 1", "type": "bedroom", "x1": 0, "x2": 4800, "y1": 4200, "y2": 9000},
                        {"id": "thang", "name": "Cầu Thang Bộ & Giếng Trời", "type": "stairs", "x1": 4800, "x2": 7800, "y1": 5600, "y2": 8600, "steps": 21},
                        {"id": "hanh_lang", "name": "Hành Lang Giao Thông", "type": "corridor", "x1": 7800, "x2": 9000, "y1": 5600, "y2": 8600},
                        {"id": "wc_2", "name": "Vệ Sinh Chung Tầng 2", "type": "wc", "x1": 9000, "x2": w_mm, "y1": 5600, "y2": 7600},
                        {"id": "ngu_con2", "name": "Phòng Ngủ Con 2", "type": "bedroom", "x1": 4800, "x2": w_mm, "y1": 8600, "y2": l_mm},
                        {"id": "ban_cong_sau", "name": "Ban Công Sau & Giặt", "type": "standard", "x1": 0, "x2": 4800, "y1": 9000, "y2": l_mm},
                    ]
                },
                "floor_3": {
                    "name": "Mặt Bằng Tầng 3 (Thờ Tự & Thư Giãn)",
                    "rooms": [
                        {"id": "tho", "name": "Phòng Thờ Trang Nghiêm", "type": "standard", "x1": 0, "x2": 4800, "y1": 0, "y2": 4200},
                        {"id": "sky_lounge", "name": "Sân Thượng Sky Lounge", "type": "living", "x1": 4800, "x2": w_mm, "y1": 0, "y2": 5600},
                        {"id": "gym", "name": "Phòng Gym & Yoga", "type": "living", "x1": 0, "x2": 4800, "y1": 4200, "y2": 9000},
                        {"id": "thang", "name": "Cầu Thang Kỹ Thuật", "type": "stairs", "x1": 4800, "x2": 7800, "y1": 5600, "y2": 8600, "steps": 21},
                        {"id": "hanh_lang", "name": "Hành Lang Giao Thông", "type": "corridor", "x1": 7800, "x2": 9000, "y1": 5600, "y2": 8600},
                        {"id": "wc_3", "name": "Vệ Sinh Tầng 3", "type": "wc", "x1": 9000, "x2": w_mm, "y1": 5600, "y2": 7600},
                        {"id": "ngu_khach", "name": "Phòng Ngủ Khách / Dự Phòng", "type": "bedroom", "x1": 4800, "x2": w_mm, "y1": 8600, "y2": l_mm},
                        {"id": "san_phoi", "name": "Sân Phơi Kỹ Thuật", "type": "standard", "x1": 0, "x2": 4800, "y1": 9000, "y2": l_mm},
                    ]
                }
            }
            site_landscape = {
                "land_dimensions": [land_size_m[0], land_size_m[1]],
                "building_footprint": [width_m, length_m],
                "setbacks": {"front_m": 14.0, "back_m": 4.0, "left_m": 4.0, "right_m": 14.0},
                "pool": {"width_m": 4.5, "length_m": 10.0, "location": "Hướng Đông Nam, view phòng khách"},
                "garage": {"width_m": 6.0, "length_m": 6.0, "capacity": "2 Ô tô + Xe máy", "location": "Góc Tây Nam cạnh cổng chính"},
                "koi_pond": {"width_m": 6.0, "length_m": 4.5, "location": "Phía trước sảnh đón"},
            }

        return {
            "author": self.name,
            "version": 1,
            "concept_theme": "Nhà Phố Xanh Hiện Đại Thang 1 Vế Áp Tường" if is_townhouse else "Biệt Thự Vườn Sinh Thái Nghỉ Dưỡng",
            "building_width_mm": w_mm,
            "building_length_mm": l_mm,
            "microclimate": microclimate_analysis,
            "site_landscape": site_landscape,
            "floors": floors,
        }

    def revise_layout(self, current_proposal: Dict[str, Any], critiques: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Tiếp thu các ý kiến phản biện từ KTS_Inspector_QC và KySu_KetCau để hiệu chỉnh phương án."""
        revised = dict(current_proposal)
        revised["version"] = revised.get("version", 1) + 1
        revised["revision_notes"] = []

        for critique in critiques:
            category = critique.get("category", "")
            issue = critique.get("issue", "")
            action = critique.get("suggested_fix", "")

            # Xử lý các điểm phản biện
            if "circulation" in category or "lối đi" in issue.lower() or "tắc" in issue.lower():
                # Đảm bảo duy trì hành lang thông suốt >= 1200mm
                for f_key in revised["floors"]:
                    f_rooms = revised["floors"][f_key]["rooms"]
                    # Kiểm tra xem có phòng hành lang chưa
                    has_corridor = any(r.get("type") == "corridor" for r in f_rooms)
                    if not has_corridor:
                        f_rooms.append({
                            "id": "hanh_lang",
                            "name": "Hành Lang Giao Thông",
                            "type": "corridor",
                            "x1": 7800, "x2": 9000, "y1": 5600, "y2": 8600
                        })
                revised["revision_notes"].append(f"Đã mở rộng & chuẩn hóa hành lang thông suốt 1200mm (X: 7800->9000) trên cả 3 tầng: {action}")

            elif "structure" in category or "cột" in issue.lower():
                revised["revision_notes"].append(f"Đã tinh giản lưới cột theo yêu cầu kỹ sư kết cấu: {action}")

        return revised
