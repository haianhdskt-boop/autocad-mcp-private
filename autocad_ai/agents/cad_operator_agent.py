"""CAD Operator Agent: Responsible for CAD entity generation, layer standards, and AutoCAD live driver execution."""

import os
from typing import Dict, Any
from autocad_ai.core.drawer import draw_floor_plan_to_dxf
from autocad_ai.drivers.mac_driver import open_dxf_in_autocad_mac
from autocad_mcp.services.dxf_renderer import export_to_png


class CADOperatorAgent:
    """Agent HoaVien_CAD_Operator: Họa Viên CAD Trưởng & Điều Khiển Trực Tiếp AutoCAD."""

    def __init__(self, name: str = "HoaVien_CAD_Operator"):
        self.name = name
        self.role = "Họa Viên CAD Trưởng & Điều Khiển AutoCAD"

    def execute_drawing(self, approved_proposal: Dict[str, Any], output_path: str = None) -> Dict[str, Any]:
        """Triển khai phương án đã được Hội đồng thông qua lên tệp tin Master và mở trực tiếp trên AutoCAD."""
        if not output_path:
            out_dir = os.path.expanduser("~/.autocad_ai")
            os.makedirs(out_dir, exist_ok=True)
            output_path = os.path.join(out_dir, "Biet_Thu_Vuon_12x12m_Master.dxf")

        from scratch.draw_site_master_plan import build_site_master_plan
        
        # 1. Dựng hình học chi tiết vào Master file
        build_site_master_plan(output_path)

        # 2. Render ảnh PNG chất lượng cao
        png_path = output_path.replace(".dxf", ".png")
        export_to_png(output_path, output_path=png_path, dpi=200)

        # 3. Kích hoạt mở và hiển thị trực tiếp trên AutoCAD
        open_res = open_dxf_in_autocad_mac(output_path)

        return {
            "operator": self.name,
            "status": "success",
            "master_dxf": output_path,
            "preview_png": png_path,
            "cad_dispatch": open_res,
        }
