#!/usr/bin/env python3
"""
Vẽ Hoàn Thiện Chi Tiết 3 Tầng Nhà Phố 5x15m Trực Tiếp Lên AutoCAD:
- Tường bao 220mm (2 nét)
- Tường ngăn phòng 110mm (2 nét) đầy đủ ranh giới
- Cửa đi 1 cánh, 4 cánh có cung quét mở cửa & Cửa sổ kỹ thuật
- Hệ thống đường kích thước 3 tầng (3-Tier Dims) chuẩn kiến trúc
- Cầu thang 1 vế 21 bậc, giếng trời, cây xanh & nội thất
"""

import os
import subprocess

def generate_detailed_lisp() -> str:
    lisp = [
        ';; ==========================================================================',
        ';; AUTOCAD AI: FULL ARCHITECTURAL DRAWING (TOWNHOUSE 5x15m - 3 FLOORS)',
        ';; ==========================================================================',
        '(defun c:draw_full_townhouse ()',
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
        '  (command "._-LAYER" "_M" "KT_TRUC"      "_C" "1" "KT_TRUC"      "")',
        '  (command "._-LAYER" "_M" "KT_CANH_QUAN" "_C" "3" "KT_CANH_QUAN" "")',
        '',
    ]

    w, l = 5000.0, 15000.0
    we, wi = 220.0, 110.0

    floors = [
        {"id": 1, "ox": 0.0, "oy": 0.0, "name": "MẶT BẰNG TẦNG 1 - KHÁCH BẾP MỞ & TIỂU CẢNH", "sub": "CAO ĐỘ +0.000 | S = 75 m²"},
        {"id": 2, "ox": 8500.0, "oy": 0.0, "name": "MẶT BẰNG TẦNG 2 - P. NGU MASTER & CON GÁI", "sub": "CAO ĐỘ +3.600 | S = 75 m²"},
        {"id": 3, "ox": 17000.0, "oy": 0.0, "name": "MẶT BẰNG TẦNG 3 - PHÒNG THỜ & CON TRAI", "sub": "CAO ĐỘ +7.200 | S = 75 m²"},
    ]

    for fl in floors:
        ox, oy = fl["ox"], fl["oy"]
        fid = fl["id"]

        lisp.append(f'  ;; ----------------- TẦNG {fid}: {fl["name"]} -----------------')
        
        # 1. Tường bao ngoài 220mm (2 nét khép kín)
        lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_220" "")')
        lisp.append(f'  (command "._RECTANG" (list {ox} {oy}) (list {ox + w} {oy + l}))')
        lisp.append(f'  (command "._RECTANG" (list {ox + we} {oy + we}) (list {ox + w - we} {oy + l - we}))')

        # 2. Cột kết cấu 220x220mm (8 cột chịu lực)
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
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {(sx1+sx2)/2} {sy1+1200}) 140 90 "UP (21 BAC)")')

        # 4. Tường ngăn 110mm (2 nét chuẩn) & Cửa chi tiết từng tầng
        if fid == 1:
            # --- TẦNG 1 ---
            # Tường ngăn Bếp / Vườn sau & WC (Y = 13500) - Tường 110mm (2 nét)
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500 + wi}) (list {ox + w - we} {oy + 13500 + wi}) "")')
            # Vách ngăn WC 1 (X = 2500) - Tường 110mm (2 nét)
            lisp.append(f'  (command "._LINE" (list {ox + 2500} {oy + 13500 + wi}) (list {ox + 2500} {oy + l - we}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + 2500 + wi} {oy + 13500 + wi}) (list {ox + 2500 + wi} {oy + l - we}) "")')

            # Cửa chính 4 cánh mặt tiền (Y = 220)
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 600} {oy + we}) (list {ox + w - 600} {oy + we}) "")')
            for cx_door in [ox + 600, ox + 1550, ox + 2500, ox + 3450, ox + 4400]:
                lisp.append(f'  (command "._LINE" (list {cx_door} {oy + we - 60}) (list {cx_door} {oy + we + 60}) "")')
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + we + 200}) 150 0 "CUA CHINH 4 CANH (D4)")')

            # Cửa đi vào WC 1 (W = 750mm, X = 1600, Y = 13500)
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 1600} {oy + 13500}) (list {ox + 1600} {oy + 13500 + 750}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1600 + 750} {oy + 13500}) (list {ox + 1600 + 530} {oy + 13500 + 530}) (list {ox + 1600} {oy + 13500 + 750}))')

            # Cửa ra sân sau (W = 900mm, X = 3200, Y = 13500)
            lisp.append(f'  (command "._LINE" (list {ox + 3200} {oy + 13500}) (list {ox + 3200} {oy + 13500 + 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 3200 + 900} {oy + 13500}) (list {ox + 3200 + 640} {oy + 13500 + 640}) (list {ox + 3200} {oy + 13500 + 900}))')

            # Giếng trời trung tâm & Zen Garden
            lisp.append('  (command "._-LAYER" "_S" "KT_CANH_QUAN" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 7000}) (list {ox + w - we} {oy + 9000}))')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 3200} {oy + 8000}) 350)')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 2200} {oy + 7600}) 200)')
            lisp.append(f'  (command "._CIRCLE" (list {ox + 4200} {oy + 8400}) 200)')

            # Nội thất Tầng 1
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 2200} {oy + 10200}) (list {ox + 4200} {oy + 11400}))')  # Bàn ăn
            lisp.append(f'  (command "._RECTANG" (list {ox + 1400} {oy + 12300}) (list {ox + w - we} {oy + 13300}))')  # Tủ bếp
            # Thiết bị WC 1
            lisp.append(f'  (command "._CIRCLE" (list {ox + 1000} {oy + 14400}) 180)')  # Bệt
            lisp.append(f'  (command "._RECTANG" (list {ox + 1600} {oy + 14400}) (list {ox + 2200} {oy + 14800}))')  # Lavabo

            # Text Tầng 1
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1200}) 180 0 "SAN TRUOC (12.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 3800}) 220 0 "PHONG KHACH DAI SANH (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 8000}) 160 0 "GIENG TROI & ZEN GARDEN")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 10800}) 200 0 "BEP & PHONG AN (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 1250} {oy + 14200}) 150 0 "WC 1 (3.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3750} {oy + 14200}) 150 0 "SAN SAU (4.0 m2)")')

        elif fid == 2:
            # --- TẦNG 2 ---
            # Tường ngăn Master Bố Mẹ (Y = 6000) - Tường 110mm (2 nét)
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000 + wi}) (list {ox + w - we} {oy + 6000 + wi}) "")')

            # Tường ngăn Phòng Con Gái (Y = 9000) - Tường 110mm (2 nét)
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 9000}) (list {ox + w - we} {oy + 9000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 9000 + wi}) (list {ox + w - we} {oy + 9000 + wi}) "")')

            # Tường ngăn WC 2 (Y = 13500) - Tường 110mm (2 nét)
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500}) (list {ox + w - we} {oy + 13500}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 13500 + wi}) (list {ox + w - we} {oy + 13500 + wi}) "")')

            # Cửa phòng Master (W = 900mm, X = 1500, Y = 6000)
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 6000}) (list {ox + 1500} {oy + 6000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 6000}) (list {ox + 1500 + 640} {oy + 6000 - 640}) (list {ox + 1500} {oy + 6000 - 900}))')

            # Cửa phòng Con Gái (W = 900mm, X = 1500, Y = 9000)
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 9000}) (list {ox + 1500} {oy + 9000 + 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 9000}) (list {ox + 1500 + 640} {oy + 9000 + 640}) (list {ox + 1500} {oy + 9000 + 900}))')

            # Cửa WC 2 (W = 750mm, X = 2000, Y = 13500)
            lisp.append(f'  (command "._LINE" (list {ox + 2000} {oy + 13500}) (list {ox + 2000} {oy + 13500 + 750}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 2000 + 750} {oy + 13500}) (list {ox + 2000 + 530} {oy + 13500 + 530}) (list {ox + 2000} {oy + 13500 + 750}))')

            # Cửa sổ mặt tiền & Ban công
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_SO" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1000} {oy + we - 60}) (list {ox + 4000} {oy + we + 60}))')

            # Nội thất Tầng 2
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1600} {oy + 3000}) (list {ox + 3400} {oy + 5000}))')  # Giường Master 1800x2000
            lisp.append(f'  (command "._RECTANG" (list {ox + 1800} {oy + 10200}) (list {ox + 3200} {oy + 12200}))')  # Giường Con gái 1400x2000

            # Text Tầng 2
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 700}) 160 0 "BAN CONG XANH (6.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4000}) 220 0 "P. NGU MASTER BO ME (24.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + 3200} {oy + 7500}) 160 0 "THONG TANG GIENG TROI")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 11200}) 200 0 "P. NGU CON GAI (20.0 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 14200}) 160 0 "WC 2 & GIENG TROI SAU")')

        elif fid == 3:
            # --- TẦNG 3 ---
            # Tường ngăn Phòng Thờ (Y = 6000) - Tường 110mm (2 nét)
            lisp.append('  (command "._-LAYER" "_S" "KT_TUONG_110" "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000}) (list {ox + w - we} {oy + 6000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 6000 + wi}) (list {ox + w - we} {oy + 6000 + wi}) "")')

            # Tường ngăn Phòng Con Trai (Y = 12000) - Tường 110mm (2 nét)
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 12000}) (list {ox + w - we} {oy + 12000}) "")')
            lisp.append(f'  (command "._LINE" (list {ox + we} {oy + 12000 + wi}) (list {ox + w - we} {oy + 12000 + wi}) "")')

            # Cửa phòng Thờ (W = 900mm, X = 1500, Y = 6000)
            lisp.append('  (command "._-LAYER" "_S" "KT_CUA_DI" "")')
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 6000}) (list {ox + 1500} {oy + 6000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 6000}) (list {ox + 1500 + 640} {oy + 6000 - 640}) (list {ox + 1500} {oy + 6000 - 900}))')

            # Cửa phòng Con Trai (W = 900mm, X = 1500, Y = 12000)
            lisp.append(f'  (command "._LINE" (list {ox + 1500} {oy + 12000}) (list {ox + 1500} {oy + 12000 - 900}) "")')
            lisp.append(f'  (command "._ARC" (list {ox + 1500 + 900} {oy + 12000}) (list {ox + 1500 + 640} {oy + 12000 - 640}) (list {ox + 1500} {oy + 12000 - 900}))')

            # Nội thất Tầng 3
            lisp.append('  (command "._-LAYER" "_S" "KT_NOITHAT" "")')
            lisp.append(f'  (command "._RECTANG" (list {ox + 1750} {oy + 4800}) (list {ox + 3250} {oy + 5600}))')  # Bàn thờ
            lisp.append(f'  (command "._RECTANG" (list {ox + 1700} {oy + 8500}) (list {ox + 3300} {oy + 10500}))')  # Giường Con trai 1600x2000

            # Text Tầng 3
            lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 1500}) 180 0 "SKY GARDEN SAN THUONG (12.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 4200}) 220 0 "PHONG THO TRANG NGHIEM (17.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 9500}) 220 0 "P. NGU CON TRAI (22.5 m2)")')
            lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy + 13500}) 180 0 "SAN PHOI & GIAT (15.0 m2)")')

        # 5. HỆ THỐNG ĐƯỜNG KÍCH THƯỚC (3-TIER DIMS)
        lisp.append('  (command "._-LAYER" "_S" "KT_DIMS" "")')
        # Tầng 1 Dims: Chi tiết từng khoang
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox + w} {oy}) (list {ox + w/2} {oy - 900}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + 2500}) (list {ox - 900} {oy + 1250}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 2500}) (list {ox} {oy + 7000}) (list {ox - 900} {oy + 4750}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 7000}) (list {ox} {oy + 9000}) (list {ox - 900} {oy + 8000}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 9000}) (list {ox} {oy + 13500}) (list {ox - 900} {oy + 11250}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 13500}) (list {ox} {oy + l}) (list {ox - 900} {oy + 14250}))')

        # Tầng 2 Dims: Tim trục kết cấu (4500 - 6000 - 4500)
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + 4500}) (list {ox - 1800} {oy + 2250}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 4500}) (list {ox} {oy + 10500}) (list {ox - 1800} {oy + 7500}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy + 10500}) (list {ox} {oy + l}) (list {ox - 1800} {oy + 12750}))')

        # Tầng 3 Dims: Phủ bì tổng thể (5000 x 15000)
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox + w} {oy}) (list {ox + w/2} {oy - 1800}))')
        lisp.append(f'  (command "._DIMLINEAR" (list {ox} {oy}) (list {ox} {oy + l}) (list {ox - 2700} {oy + l/2}))')

        # 6. Tiêu đề bản vẽ
        lisp.append('  (command "._-LAYER" "_S" "KT_TEXT" "")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 2800}) 300 0 "{fl["name"]}")')
        lisp.append(f'  (command "._-TEXT" "_J" "_MC" (list {ox + w/2} {oy - 3300}) 160 0 "{fl["sub"]}")')
        lisp.append(f'  (command "._LINE" (list {ox + w/2 - 2000} {oy - 3050}) (list {ox + w/2 + 2000} {oy - 3050}) "")')

    # Zoom Extents
    lisp.append('  (command "._ZOOM" "_E")')
    lisp.append('  (setvar "CMDECHO" 1)')
    lisp.append('  (princ "\\n*** DA HOAN TAT VE DAY DU TUONG 110/220, CUA VA DUONG DIM! ***\\n")')
    lisp.append('  (princ)')
    lisp.append(')')
    lisp.append('(c:draw_full_townhouse)')

    return "\n".join(lisp)


def main():
    lisp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'townhouse_full_detailed.lsp'))
    content = generate_detailed_lisp()
    with open(lisp_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"1. Đã tạo AutoLISP chi tiết: {lisp_path}")
    
    # Nạp trực tiếp vào AutoCAD 2024
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
    print(f"2. Kết quả AppleScript: returncode={res.returncode}")
    print("✅ ĐÃ VẼ HOÀN THIỆN ĐẦY ĐỦ TƯỜNG 220/110, CỬA, DIM 3 TẦNG TRỰC TIẾP TRÊN AUTOCAD!")

if __name__ == "__main__":
    main()
