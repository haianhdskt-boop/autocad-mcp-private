"""Windows Driver: Communicates directly with AutoCAD Windows (2021-2026) via COM."""

import sys
import os
from typing import Dict, Any, List


def is_windows() -> bool:
    """Check if running on Windows OS."""
    return sys.platform.startswith("win")


def dispatch_to_autocad_win(commands: List[str]) -> Dict[str, Any]:
    """Execute command list directly in active AutoCAD Windows."""
    if not is_windows():
        cmd_dir = os.path.expanduser("~/.autocad_ai")
        os.makedirs(cmd_dir, exist_ok=True)
        scr_file = os.path.join(cmd_dir, "live_command_win.scr")
        with open(scr_file, "w", encoding="utf-8") as f:
            f.write("\n".join(commands) + "\n\n")

        return {
            "status": "warning",
            "message": "Current environment is not Windows. Script generated and saved for Windows AutoCAD.",
            "script_file": scr_file,
            "command_count": len(commands),
        }

    try:
        import win32com.client
    except ImportError:
        return {
            "status": "error",
            "message": "pywin32 library is required on Windows. Run: pip install pywin32",
        }

    try:
        # Multi-CAD Auto-Detection on Windows:
        # 1. Autodesk AutoCAD (2021-2026)
        # 2. ZWSOFT ZWCAD (2021-2026)
        # 3. Gstarsoft GstarCAD
        # 4. Bricsys BricsCAD
        # 5. VinaCAD / EnjiCAD / IntelliCAD
        prog_ids = [
            "AutoCAD.Application",
            "AutoCAD.Application.25.1",  # 2026
            "AutoCAD.Application.25.0",  # 2025
            "AutoCAD.Application.24.3",  # 2024
            "AutoCAD.Application.24.2",  # 2023
            "AutoCAD.Application.24.1",  # 2022
            "AutoCAD.Application.24.0",  # 2021
            "ZWCAD.Application",         # ZWCAD
            "ZWCAD.Application.2025",
            "ZWCAD.Application.2024",
            "GstarCAD.Application",      # GstarCAD
            "BricsCADApp.AcadApplication", # BricsCAD
            "VinaCAD.Application",       # VinaCAD
            "EnjiCAD.Application",       # EnjiCAD
            "IntelliCAD.Application",    # IntelliCAD engine
        ]
        acad = None
        active_cad_name = "AutoCAD"
        for pid in prog_ids:
            try:
                acad = win32com.client.GetActiveObject(pid)
                if acad:
                    active_cad_name = pid.split(".")[0]
                    break
            except Exception:
                continue

        if not acad:
            # Fallback dispatch
            try:
                acad = win32com.client.Dispatch("AutoCAD.Application")
                acad.Visible = True
            except Exception:
                for alt_pid in ("ZWCAD.Application", "GstarCAD.Application", "BricsCADApp.AcadApplication"):
                    try:
                        acad = win32com.client.Dispatch(alt_pid)
                        acad.Visible = True
                        active_cad_name = alt_pid.split(".")[0]
                        break
                    except Exception:
                        continue

        if not acad:
            return {
                "status": "error",
                "message": "Không tìm thấy phần mềm CAD nào đang mở (AutoCAD, ZWCAD, GstarCAD, VinaCAD, EnjiCAD). Hãy mở phần mềm CAD của bạn trước.",
            }

        doc = acad.ActiveDocument

        for cmd in commands:
            c = cmd.strip()
            if c and not c.startswith(";;"):
                doc.SendCommand(c + "\n")

        return {
            "status": "success",
            "message": "Commands executed live on AutoCAD Windows.",
            "command_count": len(commands),
            "active_doc": doc.Name,
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to execute commands on AutoCAD Windows: {str(e)}",
        }


def open_dxf_in_autocad_win(dxf_path: str) -> Dict[str, Any]:
    """Open a DXF file directly on Windows using os.startfile."""
    if not os.path.exists(dxf_path):
        return {"status": "error", "message": f"File not found: {dxf_path}"}
    
    if not is_windows():
        return {
            "status": "warning",
            "message": f"Không phải Windows. Tệp DXF đã lưu tại: {dxf_path}",
            "dxf_file": dxf_path
        }
    
    try:
        os.startfile(dxf_path)
        return {
            "status": "success",
            "message": f"Đã xuất file DXF và gọi Windows mở tệp {dxf_path} (chạy ngầm, không gõ phím).",
            "dxf_file": dxf_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi khi mở tệp trên Windows: {str(e)}"
        }
