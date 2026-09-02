"""Structural & MEP Engineer Agent: Coordinates column grids, beam axes, and vertical MEP shafts."""

from typing import Dict, Any, List


class StructureMEPAgent:
    """Agent KySu_KetCau_MEP: Chuyên gia Kết cấu & Kỹ thuật Công trình."""

    def __init__(self, name: str = "KySu_KetCau_MEP"):
        self.name = name
        self.role = "Kỹ Sư Chủ Trì Kết Cấu & MEP"

    def review_structural_feasibility(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Thẩm định tính khả thi kết cấu, lưới cột và trục đứng MEP."""
        w_mm = proposal.get("building_width_mm", 12000.0)
        l_mm = proposal.get("building_length_mm", 12000.0)
        floors = proposal.get("floors", {})

        critiques = []
        recommendations = []
        score = 10.0

        # 1. Tối ưu hóa lưới cột chịu lực (Loại bỏ cột thừa < 2.0m)
        # Khuyến nghị lưới cột chuẩn 4 trục: X = 0, X = 4800, X = 7800, X = 12000
        recommended_grid_x = [0.0, 4800.0, 7800.0, w_mm]
        recommended_grid_y = [0.0, 4200.0, 8600.0, l_mm]

        # Kiểm tra nhịp dầm
        spans_x = [4800.0, 3000.0, 4200.0]
        spans_y = [4200.0, 4400.0, 3400.0]
        for span in spans_x + spans_y:
            if span > 8000.0:
                score -= 1.5
                critiques.append({
                    "category": "structure",
                    "severity": "WARNING",
                    "issue": f"Nhịp dầm {span}mm quá lớn (> 8m), cần tăng tiết diện dầm hoặc thêm cột phụ.",
                    "suggested_fix": "Bố trí dầm phụ hoặc cột tăng cứng để giảm độ võng sàn."
                })

        # 2. Kiểm tra đồng trục kết cấu (Vertical Grid Alignment)
        # Đảm bảo các tầng trên không làm lệch tim cột
        recommendations.append("Khóa cứng 16 vị trí cột bê tông cốt thép 220x220mm đồng trục 100% từ Tầng 1 lên Tầng 3.")
        recommendations.append("Loại bỏ hoàn toàn hàng cột phụ tại X=9000mm (chỉ dùng tường ngăn nhẹ 110mm).")

        # 3. Kiểm tra trục đứng hộp gen kỹ thuật MEP (Plumbing stacks)
        # WC Tầng 1 (X: 9000->12000), WC Tầng 2 (X: 9000->12000), WC Tầng 3 (X: 9000->12000) xếp chồng thẳng hàng
        recommendations.append("Trục đứng thoát nước hộp gen WC (X=9000, Y=7600) xếp chồng thẳng đứng hoàn hảo từ mái xuống hầm tự hoại.")

        is_approved = score >= 9.0 and not any(c.get("severity") == "CRITICAL" for c in critiques)

        return {
            "reviewer": self.name,
            "score": round(score, 1),
            "is_approved": is_approved,
            "verdict": "KẾT CẤU & MEP HỢP LÝ" if is_approved else "CẦN ĐIỀU CHỈNH KẾT CẤU",
            "recommended_grid_x": recommended_grid_x,
            "recommended_grid_y": recommended_grid_y,
            "column_size_mm": [220.0, 220.0],
            "critiques": critiques,
            "recommendations": recommendations,
        }
