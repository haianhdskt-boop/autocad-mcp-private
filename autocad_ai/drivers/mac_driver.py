"""macOS Driver: Communicates directly with AutoCAD for Mac (2021-2026).

IMPORTANT: Dùng clipboard paste (Cmd+V) thay vì keystroke để tránh lỗi
bộ gõ tiếng Việt (Unikey/Telex) chuyển đổi ký tự khi gõ.
Ví dụ: keystroke "_SCRIPT" bị bộ gõ biến thành "_CRỊPT".
"""

import os
import subprocess
from typing import Dict, Any, List


def _paste_text_to_cad(text: str) -> None:
    """Paste text into active CAD app via clipboard (bypasses Vietnamese IME).

    Thay vì dùng `keystroke` (bị bộ gõ tiếng Việt can thiệp),
    ta copy text vào clipboard rồi Cmd+V paste trực tiếp.
    """
    # Copy text to macOS clipboard
    proc = subprocess.run(
        ["pbcopy"], input=text.encode("utf-8"), capture_output=True
    )
    # Cmd+V paste
    subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to keystroke "v" using command down'],
        capture_output=True, text=True,
    )


def is_autocad_running_mac() -> bool:
    """Check if AutoCAD or any DWG CAD (ZWCAD, BricsCAD) is running on macOS.

    Dùng System Events thay vì pgrep để detect chính xác hơn trên macOS.
    """
    try:
        result = subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to get name of every process '
             'whose background only is false'],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            procs = result.stdout.lower()
            for cad in ("autocad", "zwcad", "bricscad", "gstarcad", "vinacad", "enjicad"):
                if cad in procs:
                    return True
    except Exception:
        pass

    # Fallback: pgrep
    for cad_app in ("AutoCAD", "ZWCAD", "BricsCAD"):
        try:
            res = subprocess.run(["pgrep", "-if", cad_app], capture_output=True, text=True)
            if res.returncode == 0 and len(res.stdout.strip()) > 0:
                return True
        except Exception:
            continue
    return False


def dispatch_to_autocad_mac(commands: List[str]) -> Dict[str, Any]:
    """Execute command list directly in active AutoCAD / ZWCAD / BricsCAD for Mac.

    Workflow:
    1. Ghi danh sách lệnh vào file .scr
    2. Activate cửa sổ CAD
    3. Dùng clipboard paste gõ lệnh _FILEDIA 0 (tắt dialog)
    4. Paste lệnh _SCRIPT + đường dẫn file .scr
    5. Bật lại _FILEDIA 1 sau khi xong
    """
    if not commands:
        return {"status": "error", "message": "No commands provided"}

    cmd_dir = os.path.expanduser("~/.autocad_ai")
    os.makedirs(cmd_dir, exist_ok=True)
    scr_file = os.path.join(cmd_dir, "live_command.scr")

    # Giữ lại blank lines cho TEXT command termination
    scr_lines = []
    for cmd in commands:
        if cmd.strip() == "":
            scr_lines.append("")  # Blank line = Enter (exit TEXT/LINE)
        else:
            scr_lines.append(cmd.strip())
    scr_content = "\n".join(scr_lines) + "\n\n"

    with open(scr_file, "w", encoding="utf-8") as f:
        f.write(scr_content)

    is_running = is_autocad_running_mac()
    if not is_running:
        return {
            "status": "warning",
            "message": "Phần mềm CAD (AutoCAD/ZWCAD/BricsCAD) chưa mở. File kịch bản đã được lưu sẵn.",
            "script_file": scr_file,
            "command_count": len([l for l in scr_lines if l.strip()]),
            "how_to_run": f"Mở CAD lên -> Gõ lệnh 'SCRIPT' -> Chọn file '{scr_file}'",
        }

    try:
        # Step 1: Activate CAD window
        activate_script = '''
        tell application "System Events"
            set cadProc to (first process whose name contains "AutoCAD" \
                or name contains "ZWCAD" or name contains "BricsCAD")
            set frontmost of cadProc to true
            delay 0.5
            -- Raise the drawing window (not dialogs)
            repeat with w in windows of cadProc
                if name of w contains ".dwg" or name of w contains "Drawing" then
                    try
                        perform action "AXRaise" of w
                    end try
                    exit repeat
                end if
            end repeat
            delay 0.3
        end tell
        '''
        subprocess.run(["osascript", "-e", activate_script],
                        capture_output=True, text=True, timeout=5)

        # Step 2: Cancel any pending command with Escape
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to key code 53'],  # Escape
            capture_output=True, text=True,
        )
        subprocess.run(
            ["osascript", "-e", 'delay 0.3'],
            capture_output=True, text=True,
        )

        # Step 3: Tắt FILEDIA để SCRIPT không mở file dialog
        # Dùng clipboard paste thay vì keystroke
        _paste_text_to_cad("_FILEDIA\n0\n")
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to keystroke return'],
            capture_output=True, text=True,
        )
        subprocess.run(["osascript", "-e", 'delay 0.5'],
                        capture_output=True, text=True)

        # Step 4: Chạy SCRIPT với đường dẫn file (qua clipboard paste)
        script_cmd = f"_SCRIPT\n{scr_file}\n"
        _paste_text_to_cad(script_cmd)
        subprocess.run(
            ["osascript", "-e",
             'tell application "System Events" to keystroke return'],
            capture_output=True, text=True,
        )

        return {
            "status": "success",
            "message": "Đã thực thi trực tiếp trên màn hình CAD (macOS) qua clipboard paste.",
            "command_count": len([l for l in scr_lines if l.strip()]),
            "script_file": scr_file,
        }

    except Exception as e:
        return {
            "status": "partial_success",
            "message": f"Script saved to {scr_file}, trigger note: {str(e)}",
            "script_file": scr_file,
            "how_to_run": f"In AutoCAD, type SCRIPT and choose {scr_file}",
        }


def _find_mac_cad_app() -> str | None:
    """Detect installed or running CAD application on macOS."""
    import glob
    # 1. Check running CAD process
    try:
        res = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get POSIX path of (file of every process whose name contains "AutoCAD" or name contains "ZWCAD" or name contains "BricsCAD")'],
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0 and res.stdout.strip():
            paths = [p.strip() for p in res.stdout.strip().split(",") if p.strip()]
            if paths:
                return paths[0]
    except Exception:
        pass

    # 2. Check standard Applications paths
    patterns = [
        "/Applications/Autodesk/AutoCAD */AutoCAD *.app",
        "/Applications/AutoCAD *.app",
        "/Applications/ZWCAD *.app",
        "/Applications/BricsCAD *.app",
    ]
    for pat in patterns:
        matches = glob.glob(pat)
        if matches:
            return sorted(matches, reverse=True)[0]
    return None


def open_dxf_in_autocad_mac(dxf_path: str) -> Dict[str, Any]:
    """Open a DXF file in AutoCAD for Mac and bring AutoCAD to foreground."""
    if not os.path.exists(dxf_path):
        return {"status": "error", "message": f"File not found: {dxf_path}"}
    
    cad_app = _find_mac_cad_app()
    try:
        if cad_app:
            subprocess.run(["open", "-a", cad_app, dxf_path], check=True)
        else:
            subprocess.run(["open", dxf_path], check=True)
            
        # Bring CAD window to front
        activate_script = '''
        tell application "System Events"
            set cadProc to (first process whose name contains "AutoCAD" or name contains "ZWCAD" or name contains "BricsCAD")
            set frontmost of cadProc to true
        end tell
        '''
        subprocess.run(["osascript", "-e", activate_script], capture_output=True, text=True, timeout=5)

        return {
            "status": "success",
            "message": f"Đã mở file DXF {dxf_path} trên AutoCAD và đưa cửa sổ lên màn hình chính.",
            "dxf_file": dxf_path,
            "cad_app": cad_app or "Default System CAD Viewer"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi khi mở tệp trên CAD: {str(e)}"
        }
