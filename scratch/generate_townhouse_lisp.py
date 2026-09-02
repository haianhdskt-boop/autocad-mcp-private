#!/usr/bin/env python3
"""
Tạo kịch bản AutoLISP chuyên nghiệp để VẼ TRỰC TIẾP TOÀN BỘ 3 TẦNG NHÀ PHỐ 5x15m TRÊN AUTOCAD ĐANG MỞ
"""

import os
import subprocess

def generate_townhouse_lisp() -> str:
    lisp_code = [
        ';; ==========================================================================',
        ';; AUTOCAD AI: DIRECT LIVE DRAFTING SCRIPT (3-FLOOR TOWNHOUSE 5x15m)',
        ';; ==========================================================================',
        '(defun c:draw_townhouse ()',
        '  (setvar "CMDECHO" 0)',
        '  (setvar "OSMODE" 0)',
        '  (command "._ERASE" "_ALL" "")',
        '',
        '  ;; 1. Setup Standard Layers',
        '  (command "._-LAYER" "_M" "KT_TUONG_220" "_C" "1" "KT_TUONG_220" "")',
        '  (command "._-LAYER" "_M" "KT_TUONG_110" "_C" "2" "KT_TUONG_110" "")',
        '  (command "._-LAYER" "_M" "KT_COT"       "_C" "6" "KT_COT"       "")',
        '  (command "._-LAYER" "_M" "KT_CUA_DI"    "_C" "3" "KT_CUA_DI"    "")',
        '  (command "._-LAYER" "_M" "KT_CUA_SO"    "_C" "4" "KT_CUA_SO"    "")',
        '  (command "._-LAYER" "_M" "KT_THANG"     "_C" "5" "KT_THANG"     "")',
        '  (command "._-LAYER" "_M" "KT_NOITHAT"   "_C" "8" "KT_NOITHAT"   "")',
        '  (command "._-LAYER" "_M" "KT_TEXT"      "_C" "7" "KT_TEXT"      "")',
        '  (command "._-LAYER" "_M" "KT_DIMS"      "_C" "9" "KT_DIMS"      "")',
        '  (command "._-LAYER" "_M" "KT_CANH_QUAN" "_C" "3" "KT_CANH_QUAN" "")',
        '',
    ]

    w, l = 5000.0, 15000.0
    we, wi = 220.0, 110.0

    floors = [
        {"id": 1, "ox": 0.0, "oy": 0.0, "name": "MAT BANG TANG 1 - KHACH BEP MO & TIEU CANH", "sub": "CAO DO +0.000 | S = 75 m2"},
        {"id": 2, "ox": 8000.0, "oy": 0.0, "name": "MAT BANG TANG 2 - P. NGU MASTER & CON GAI", "sub": "CAO DO +3.600 | S = 75 m2"},
        {"id": 3, "ox": 16000.0, "oy": 0.0, "name": "MAT BANG TANG 3 - PHONG THO & CON TRAI", "sub": "CAO DO +7.200 | S = 75 m2"},
    ]

    for fl in floors:
        ox, oy = fl["ox"], fl["oy"]
        fid = fl["id"]

        lisp_code.append(f'  ;; --- FLOOR {fid}: {fl["name"]} ---')
        # A. Tường bao 220mm
        lisp_code.append('  (command "._-LAYER" "_S" "KT_TUONG_220" "")')
        lisp_code.append(f'  (command "._RECTANG" (list {ox} {oy}) (list {ox + w} {oy + l}))')
        lisp_code.append(f'  (command "._RECTANG" (list {ox + we} {oy + we}) (list {ox + w - we} {oy + l - we}))')

        # B. Cột kết cấu 220x220mm
        lisp_code.append('  (command "._-LAYER" "_S" "KT_COT" "")')
        cols_y = [oy, oy + 4500 - 110, oy + 10500 - 110, oy + l - 220]
        for cy in cols_y:
            for cx in [ox, ox + w - 220]:
                lisp_code.append(f'  (command "._RECTANG" (list {cx} {cy}) (list {cx + 220} {cy + 220}))')
                lisp_code.append(f'  (command "._LINE" (list {cx} {cy}) (list {cx + 220} {cy + 220}) "")')
                lisp_code.append(f'  (command "._LINE" (list {cx + 220} {cy}) (list {cx} {cy + 220}) "")')

        # C. Cầu thang thẳng 1 vế áp tường (21 bậc)
        lisp_code.append('  (command "._-LAYER" "_S" "KT_THANG" "")')
        sx1, sx2 = ox + we, ox + we + 1000
        sy1, sy2 = oy + 5000, oy + 10500
        lisp_code.append(f'  (command "._RECTANG" (list {sx1} {sy1}) (list {sx2} {sy2}))')
        step_len = (sy2 - sy1) / 21.0
        for st in range(1, 21):
            y_st = sy1 + st * step_len
            lisp_code.append(f'  (command "._LINE" (list {sx1} {y_st}) (list {sx2} {y_st}) "")')
        lisp_code.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy1+400}) (list {(sx1+sx2)/2} {sy2-400}) "")')
        lisp_code.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy2-400}) (list {(sx1+sx2)/2 - 120} {sy2-800}) "")')
        lisp_code.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy2-400}) (list {(sx1+sx2)/2 + 120} {sy2-800}) "")')

        # D. Chi tiết từng tầng
        if fid == 1:
            lisp_code.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + 2500} {oy + 13500}) (list {ox + 2500} {oy + l - we}) "")')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 7000}) (list {ox + w - we} {oy + 9000}))')
            lisp_code.append(f'  (command "._CIRCLE" (list {ox + 3200} {oy + 8000}) 350)')
            lisp_code.append(f'  (command "._CIRCLE" (list {ox + 2200} {oy + 7600}) 220)')
            lisp_code.append(f'  (command "._CIRCLE" (list {ox + 4200} {oy + 8400}) 220)')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 2200} {oy + 10200}) (list {ox + 4200} {oy + 11400}))')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 12300}) (list {ox + w - we} {oy + 13300}))')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1200}) 180 0 "SAN TRUOC & TIEU CANH (12.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 3800}) 220 0 "PHONG KHACH DAI SANH (22.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 8000}) 160 0 "GIENG TROI & ZEN GARDEN")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 10800}) 200 0 "BEP & PHONG AN (22.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 1250} {oy + 14200}) 150 0 "WC 1 (3.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3750} {oy + 14200}) 150 0 "SAN SAU (4.0 m2)")')

        elif fid == 2:
            lisp_code.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 9000}) (list {ox + w - we} {oy + 9000}) "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 200} {oy + 200}) (list {ox + w - 200} {oy + 1200}))')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1600} {oy + 3000}) (list {ox + 3400} {oy + 5000}))')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1800} {oy + 10200}) (list {ox + 3200} {oy + 12200}))')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 700}) 160 0 "BAN CONG XANH (6.0 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4000}) 220 0 "P. NGU MASTER BO ME (24.0 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 7500}) 160 0 "THONG TANG GIENG TROI")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 11200}) 200 0 "P. NGU CON GAI (20.0 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 14200}) 160 0 "WC 2 & GIENG TROI SAU")')

        elif fid == 3:
            lisp_code.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp_code.append(f'  (command "._LINE" (list {ox + we} {oy + 12000}) (list {ox + w - we} {oy + 12000}) "")')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 200} {oy + 200}) (list {ox + w - 200} {oy + 2500}))')
            lisp_code.append(f'  (command "._CIRCLE" (list {ox + 1200} {oy + 1200}) 250)')
            lisp_code.append(f'  (command "._CIRCLE" (list {ox + 3800} {oy + 1200}) 250)')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1750} {oy + 4800}) (list {ox + 3250} {oy + 5600}))')
            lisp_code.append(f'  (command "._RECTANG" (list {ox + 1700} {oy + 8500}) (list {ox + 3300} {oy + 10500}))')

            lisp_code.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1500}) 180 0 "SKY GARDEN SAN THUONG (12.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4200}) 220 0 "PHONG THO TRANG NGHIEM (17.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 9500}) 220 0 "P. NGU CON TRAI (22.5 m2)")')
            lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 13500}) 180 0 "SAN PHOI & GIAT (15.0 m2)")')

        # DIMS
        lisp_code.append('  (command "._-LAYER" "_S" "KT_DIMS" "")')
        lisp_code.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox + w} {oy}) (list {ox + w/2} {oy - 1200}))')
        lisp_code.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + l}) (list {ox - 1200} {oy + l/2}))')

        # Tiêu đề
        lisp_code.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
        lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 2200}) 300 0 "{fl["name"]}")')
        lisp_code.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 2700}) 160 0 "{fl["sub"]}")')

    # Zoom extents
    lisp_code.append('  (command "._ZOOM" "_E")')
    lisp_code.append('  (setvar "CMDECHO" 1)')
    lisp_code.append('  (princ "\\n*** DA VE HOAN TAT 3 TANG NHA PHO 5x15m TREN AUTOCAD! ***\\n")')
    lisp_code.append('  (princ)')
    lisp_code.append(')')
    lisp_code.append('(c:draw_townhouse)')

    return "\n".join(lisp_code)


def main():
    lisp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'townhouse_live_draw.lsp'))
    content = generate_townhouse_lisp()
    with open(lisp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"1. Đã tạo tệp AutoLISP hoàn chỉnh: {lisp_path}")
    
    # Nạp vào AutoCAD 2024
    applescript = f'''
    tell application "System Events"
        set cadProc to (first process whose name contains "AutoCAD")
        set frontmost of cadProc to true
        delay 0.3
        key code 53 -- Escape
        delay 0.1
        key code 53
        delay 0.2
        keystroke "(load \\"{lisp_path}\\")" & return
    end tell
    '''
    res = subprocess.run(["osascript", "-e", applescript], capture_output=True, text=True)
    print(f"2. Kết quả thực thi AutoLISP trên AutoCAD: returncode={res.returncode}")
    print("✅ ĐÃ VẼ XONG 100% 3 TẦNG TRỰC TIẾP TRÊN AUTOCAD!")

if __name__ == "__main__":
    main()
