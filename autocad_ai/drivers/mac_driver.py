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


def dispatch_to_autocad_mac(commands: List[str], batch_size: int = 25) -> Dict[str, Any]:
    """Execute command list directly in active AutoCAD / ZWCAD / BricsCAD for Mac via direct AppleScript keystrokes."""
    if not commands:
        return {"status": "error", "message": "No commands provided"}

    is_running = is_autocad_running_mac()
    if not is_running:
        return {
            "status": "warning",
            "message": "Phần mềm CAD (AutoCAD/ZWCAD/BricsCAD) chưa mở. Vui lòng mở CAD trước.",
            "command_count": len(commands),
        }

    try:
        import time

        # 1. Activate CAD và Escape lệnh cũ
        init_script = '''
        tell application "System Events"
            set cadProc to (first process whose name contains "AutoCAD" \
                or name contains "ZWCAD" or name contains "BricsCAD")
            set frontmost of cadProc to true
            delay 0.2
            key code 53 -- Escape
            delay 0.1
            key code 53
        end tell
        '''
        subprocess.run(["osascript", "-e", init_script], capture_output=True, text=True, timeout=5)
        time.sleep(0.2)

        # 2. Gửi từng batch lệnh CAD trực tiếp
        total = len(commands)
        for i in range(0, total, batch_size):
            batch = commands[i:i + batch_size]
            lines = []
            for cmd in batch:
                c = cmd.strip()
                if not c:
                    lines.append('keystroke return')
                else:
                    escaped = c.replace('"', '\\"')
                    lines.append(f'keystroke "{escaped}" & return')
            
            batch_script = f'''
            tell application "System Events"
                set cadProc to (first process whose name contains "AutoCAD" \
                    or name contains "ZWCAD" or name contains "BricsCAD")
                set frontmost of cadProc to true
                {chr(10).join(lines)}
            end tell
            '''
            subprocess.run(["osascript", "-e", batch_script], capture_output=True, text=True, timeout=10)
            time.sleep(0.12)

        # 3. Zoom Extents
        final_script = '''
        tell application "System Events"
            set cadProc to (first process whose name contains "AutoCAD" \
                or name contains "ZWCAD" or name contains "BricsCAD")
            set frontmost of cadProc to true
            delay 0.2
            key code 53
            keystroke "._zoom _e" & return
        end tell
        '''
        subprocess.run(["osascript", "-e", final_script], capture_output=True, text=True, timeout=5)

        return {
            "status": "success",
            "message": "Đã vẽ trực tiếp từng nét lên màn hình AutoCAD đang mở qua Direct AppleScript Keystroke!",
            "command_count": total,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi dispatch lệnh trực tiếp: {str(e)}",
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
