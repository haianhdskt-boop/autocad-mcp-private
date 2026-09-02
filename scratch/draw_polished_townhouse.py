#!/usr/bin/env python3
"""
Tinh chỉnh khoảng cách giãn cách 3 Tầng Nhà phố 5x15m & Định dạng chữ tiêu đề chuẩn mực không đè nhau
"""

import os
import subprocess

def generate_polished_lisp() -> str:
    lisp = [
        ';; ==========================================================================',
        ';; AUTOCAD AI: PERFECTLY SPACED 3-FLOOR TOWNHOUSE 5x15m',
        ';; ==========================================================================',
        '(defun c:draw_polished_townhouse ()',
        '  (setvar "CMDECHO" 0)',
        '  (setvar "OSMODE" 0)',
        '  (command "._ERASE" "_ALL" "")',
        '',
        '  ;; 1. Layers Setup',
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

    # Tăng khoảng cách giữa các tầng lên 10.000mm để các tiêu đề & DIM hoàn toàn thoáng đãng
    floors = [
        {
            "id": 1, "ox": 0.0, "oy": 0.0,
            "title_1": "MẶT BẰNG TẦNG 1",
            "title_2": "KHÁCH - BẾP MỞ & TIỂU CẢNH (+0.000)",
            "sub": "DIỆN TÍCH SÀN: 75 m² | TỶ LỆ 1/100"
        },
        {
            "id": 2, "ox": 10000.0, "oy": 0.0,
            "title_1": "MẶT BẰNG TẦNG 2",
            "title_2": "P. NGU MASTER & CON GÁI (+3.600)",
            "sub": "DIỆN TÍCH SÀN: 75 m² | TỶ LỆ 1/100"
        },
        {
            "id": 3, "ox": 20000.0, "oy": 0.0,
            "title_1": "MẶT BẰNG TẦNG 3",
            "title_2": "PHÒNG THỜ & CON TRAI (+7.200)",
            "sub": "DIỆN TÍCH SÀN: 75 m² | TỶ LỆ 1/100"
        },
    ]

    for fl in floors:
        ox, oy = fl["ox"], fl["oy"]
        fid = fl["id"]

        lisp.append(f'  ;; ----------------- TẦNG {fid} -----------------')
        
        # 1. Tường bao ngoài 220mm (2 nét)
        lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_220" "")')
        lisp.append(f'  (command "._RECTANG" (list {ox} {oy}) (list {ox + w} {oy + l}))')
        lisp.append(f'  (command "._RECTANG" (list {ox + we} {oy + we}) (list {ox + w - we} {oy + l - we}))')

        # 2. Cột kết cấu 220x220mm
        lisp.append('  (command "._-LAYER" "_S" "KT_COT" "")')
        cols_y = [oy, oy + 4500 - 110, oy + 10500 - 110, oy + l - 220]
        for cy in cols_y:
            for cx in [ox, ox + w - 220]:
                lisp.append(f'  (command "._RECTANG" (list {cx} {cy}) (list {cx + 220} {cy + 220}))')
                lisp.append(f'  (command "._LINE" (list {cx} {cy}) (list {cx + 220} {cy + 220}) "")')
                lisp.append(f'  (command "._LINE" (list {cx + 220} {cy}) (list {cx} {cy + 220}) "")')

        # 3. Cầu thang thẳng 1 vế áp tường 21 bậc (X: 0 -> 1000, Y: 5000 -> 10500)
        lisp.append('  (command "._-LAYER" "_S" "KT_THANG" "")')
        sx1, sx2 = ox + we, ox + we + 1000
        sy1, sy2 = oy + 5000, oy + 10500
        lisp.append(f'  (command "._RECTANG" (list {sx1} {sy1}) (list {sx2} {sy2}))')
        step_len = (sy2 - sy1) / 21.0
        for st in range(1, 21):
            y_st = sy1 + st * step_len
            lisp.append(f'  (command "._LINE" (list {sx1} {y_st}) (list {sx2} {y_st}) "")')
        lisp.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy1+400}) (list {(sx1+sx2)/2} {sy2-400}) "")')
        lisp.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy2-400}) (list {(sx1+sx2)/2 - 120} {sy2-800}) "")')
        lisp.append(f'  (command "._LINE" (list {(sx1+sx2)/2} {sy2-400}) (list {(sx1+sx2)/2 + 120} {sy2-800}) "")')
        lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {(sx1+sx2)/2} {sy1+1200}) 130 90 "UP (21 BAC)")')

        # 4. Tường ngăn 110mm & Cửa chi tiết
        if fid == 1:
            # TẦNG 1
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500 + wi}) (list {ox + w - we} {oy + 13500 + wi}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + 2500} {oy + 13500 + wi}) (list {ox + 2500} {oy + l - we}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + 2500 + wi} {oy + 13500 + wi}) (list {ox + 2500 + wi} {oy + l - we}) "")')

            # Cửa chính 4 cánh mặt tiền
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 600} {oy + we}) (list {ox + w - 600} {oy + we}) "")')
            for cx_door in [ox + 600, ox + 1550, ox + 2500, ox + 3450, ox + 4400]:
                lisp.append(f'  (command "._LINE" (list {cx_door} {oy + we - 50}) (list {cx_door} {oy + we + 50}) "")')

            # Cửa WC 1 & Cửa ra sân sau
            lisp.append(f'  (command "._LINE" (list {ox + 1600} {oy + 13500}) (list {ox + 1600} {oy + 13500 + 750}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1600 + 750} {oy + 13500}) (list {ox + 1600 + 530} {oy + 13500 + 530}) (list {ox + 1600} {oy + 13500 + 750}))')
            lisp.append(f'  (command "._LINE" (list {ox + 3200} {oy + 13500}) (list {ox + 3200} {oy + 13500 + 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 3200 + 900} {oy + 13500}) (list {ox + 3200 + 640} {oy + 13500 + 640}) (list {ox + 3200} {oy + 13500 + 900}))')

            # Giếng trời trung tâm
            lisp.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 7000}) (list {ox + w - we} {oy + 9000}))')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 3200} {oy + 8000}) 350)')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 2200} {oy + 7600}) 200)')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 4200} {oy + 8400}) 200)')

            # Nội thất Tầng 1
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 2200} {oy + 10200}) (list {ox + 4200} {oy + 11400}))')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 12300}) (list {ox + w - we} {oy + 13300}))')

            # Text Tầng 1
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1200}) 170 0 "SAN TRUOC (12.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 3800}) 210 0 "PHONG KHACH DAI SANH (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 8000}) 150 0 "GIENG TROI & ZEN GARDEN")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 10800}) 190 0 "BEP & PHONG AN (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 1250} {oy + 14200}) 140 0 "WC 1 (3.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3750} {oy + 14200}) 140 0 "SAN SAU (4.0 m2)")')

        elif fid == 2:
            # TẦNG 2
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000 + wi}) (list {ox + w - we} {oy + 6000 + wi}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 9000}) (list {ox + w - we} {oy + 9000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 9000 + wi}) (list {ox + w - we} {oy + 9000 + wi}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500 + wi}) (list {ox + w - we} {oy + 13500 + wi}) "")')

            # Cửa phòng Master & Con Gái
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 6000}) (list {ox + 1500} {oy + 6000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 6000}) (list {ox + 1500 + 640} {oy + 6000 - 640}) (list {ox + 1500} {oy + 6000 - 900}))')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 9000}) (list {ox + 1500} {oy + 9000 + 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 9000}) (list {ox + 1500 + 640} {oy + 9000 + 640}) (list {ox + 1500} {oy + 9000 + 900}))')
            lisp.append(f'  (command "._LINE" (list {ox + 2000} {oy + 13500}) (list {ox + 2000} {oy + 13500 + 750}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 2000 + 750} {oy + 13500}) (list {ox + 2000 + 530} {oy + 13500 + 530}) (list {ox + 2000} {oy + 13500 + 750}))')

            # Ban công & Nội thất Tầng 2
            lisp.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 200} {oy + 200}) (list {ox + w - 200} {oy + 1200}))')
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1600} {oy + 3000}) (list {ox + 3400} {oy + 5000}))')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1800} {oy + 10200}) (list {ox + 3200} {oy + 12200}))')

            # Text Tầng 2
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 700}) 150 0 "BAN CONG XANH (6.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4000}) 210 0 "P. NGU MASTER BO ME (24.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 7500}) 150 0 "THONG TANG GIENG TROI")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 11200}) 190 0 "P. NGU CON GAI (20.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 14200}) 150 0 "WC 2 & GIENG TROI SAU")')

        elif fid == 3:
            # TẦNG 3
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000 + wi}) (list {ox + w - we} {oy + 6000 + wi}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 12000}) (list {ox + w - we} {oy + 12000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 12000 + wi}) (list {ox + w - we} {oy + 12000 + wi}) "")')

            # Cửa phòng Thờ & Con Trai
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 6000}) (list {ox + 1500} {oy + 6000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 6000}) (list {ox + 1500 + 640} {oy + 6000 - 640}) (list {ox + 1500} {oy + 6000 - 900}))')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 12000}) (list {ox + 1500} {oy + 12000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 12000}) (list {ox + 1500 + 640} {oy + 12000 - 640}) (list {ox + 1500} {oy + 12000 - 900}))')

            # Sân thượng & Nội thất Tầng 3
            lisp.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 200} {oy + 200}) (list {ox + w - 200} {oy + 2500}))')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 1200} {oy + 1200}) 250)')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 3800} {oy + 1200}) 250)')
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1750} {oy + 4800}) (list {ox + 3250} {oy + 5600}))')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1700} {oy + 8500}) (list {ox + 3300} {oy + 10500}))')

            # Text Tầng 3
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1500}) 170 0 "SKY GARDEN SAN THUONG (12.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4200}) 210 0 "PHONG THO TRANG NGHIEM (17.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 9500}) 210 0 "P. NGU CON TRAI (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 13500}) 170 0 "SAN PHOI & GIAT (15.0 m2)")')

        # 5. ĐƯỜNG KÍCH THƯỚC (DIMS) PHÂN CẤP RÕ RÀNG
        lisp.append('  (command "._-LAYER" "_S" "KT_DIMS" "")')
        # Ngang đáy
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox + w} {oy}) (list {ox + w/2} {oy - 800}))')
        # Dọc trái - Chi tiết
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + 2500}) (list {ox - 800} {oy + 1250}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 2500}) (list {ox} {oy + 7000}) (list {ox - 800} {oy + 4750}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 7000}) (list {ox} {oy + 9000}) (list {ox - 800} {oy + 8000}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 9000}) (list {ox} {oy + 13500}) (list {ox - 800} {oy + 11250}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 13500}) (list {ox} {oy + l}) (list {ox - 800} {oy + 14250}))')
        # Dọc trái - Tổng thể
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + l}) (list {ox - 1700} {oy + l/2}))')

        # 6. Tiêu đề 2 dòng thoáng đãng, không bao giờ chạm nhau
        lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 1800}) 260 0 "{fl["title_1"]}")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 2300}) 170 0 "{fl["title_2"]}")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 2800}) 130 0 "{fl["sub"]}")')
        lisp.append(f'  (command "._LINE" (list {ox + w/2 - 1800} {oy - 2550}) (list {ox + w/2 + 1800} {oy - 2550}) "")')

    # Zoom Extents
    lisp.append('  (command "._ZOOM" "_E")')
    lisp.append('  (setvar "CMDECHO" 1)')
    lisp.append('  (princ "\\n*** DA VE HOAN TAT 3 TANG NHA PHO 5x15m CHUAN DEP! ***\\n")')
    lisp.append('  (princ)')
    lisp.append(')')
    lisp.append('(c:draw_polished_townhouse)')

    return "\n".join(lisp)


def main():
    lisp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'townhouse_polished.lsp'))
    content = generate_polished_lisp()
    with open(lisp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Nạp trực tiếp vào AutoCAD
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
    print(f"✅ Đã thực thi cập nhật bản vẽ chuẩn đẹp trên AutoCAD (returncode={res.returncode})")

if __name__ == "__main__":
    main()
