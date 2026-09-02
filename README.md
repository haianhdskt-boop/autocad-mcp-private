# AutoCAD AI MCP - Trợ Lý Kiến Trúc Sư Chuyên Nghiệp

[![FastMCP](https://img.shields.io/badge/MCP-FastMCP%20v4.0-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![AutoCAD](https://img.shields.io/badge/AutoCAD-2021--2026-red.svg)](https://www.autodesk.com/autocad)
[![Platforms](https://img.shields.io/badge/Platforms-macOS%20%7C%20Windows-lightgrey.svg)]()
[![License](https://img.shields.io/badge/License-MIT-blue.svg)]()

Hệ sinh thái **Model Context Protocol (MCP)** chuyên biệt hóa dành cho **Kiến Trúc Sư & Kỹ Sư Xây Dựng**. Tích hợp sẵn toàn bộ kho dữ liệu quy chuẩn kiến trúc [architecture-reference-library](https://github.com/haianhdskt-boop/architecture-reference-library) vào mã nguồn (`autocad_ai/knowledge/`), điều khiển và tương tác theo thời gian thực trên màn hình **AutoCAD (2021 - 2026)** trên cả **macOS** và **Windows**.

Toàn bộ các lệnh được chuẩn hóa sang **tiếng Việt không dấu (tiền tố `cad_`)** và ràng buộc nghiêm ngặt nguyên tắc **"Bản vẽ sạch sẽ - Không chồng đè"**.

---

## ⚡ CÀI ĐẶT 1-CHẠM TỰ ĐỘNG TỪ GITHUB (ZERO BLOAT)

### 🍎 Dành cho máy macOS (Ở nhà):
Chạy lệnh sau trong Terminal (chỉ cài module macOS, không dính mã Windows):
```bash
curl -sSL https://raw.githubusercontent.com/haianhdskt-boop/autocad-ai-mcp/main/install-mac.sh | bash
```

### 🪟 Dành cho máy Windows (Tại văn phòng):
Chạy lệnh sau trong PowerShell (chỉ cài module COM ActiveX Windows):
```powershell
irm https://raw.githubusercontent.com/haianhdskt-boop/autocad-ai-mcp/main/install-win.ps1 | iex
```

---

## 🚫 NGUYÊN TẮC RÀNG BUỘC: BẢN VẼ SẠCH SẼ - KHÔNG CHỒNG ĐÈ (ZERO-OVERLAP)

Áp dụng bắt buộc khi **VẼ (`cad_ve_moi`)**, **HOÀN THIỆN (`cad_hoan_thien_ho_so`)**, **CHỈNH SỬA (`cad_chinh_sua`)** và **KIỂM TRA (`cad_kiem_tra`)**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│             5 NGUYÊN TẮC BẢN VẼ SẠCH SẼ, MẠCH LẠC & KHÔNG CHỒNG ĐÈ          │
├───────────────────────────────────┬─────────────────────────────────────────┤
│ 1. ĐỒ NỘI THẤT - TƯỜNG XÂY        │ CẤM đồ nội thất đè/lấn vào tường xây    │
│                                   │ 110/220 (trừ hộc tủ âm tường). Giữ khe  │
│                                   │ hở an toàn >= 50 - 100mm từ mặt trong.  │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 2. TƯỜNG XÂY - ĐỒ NỘI THẤT        │ CẤM nét tường chém/đè lên thiết bị vệ   │
│                                   │ sinh, bếp, sofa, giường tủ.             │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 3. CHỮ VIẾT, GHI CHÚ & CAO ĐỘ     │ CẤM chữ ghi chú đè lên nhau. CẤM chữ đè │
│                                   │ lên nét vẽ kiến trúc, thiết bị, hatch.  │
│                                   │ Text phải đặt ở vùng đệm thoáng đãng.   │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 4. ĐƯỜNG KÍCH THƯỚC (DIM)         │ CẤM các đường DIM đè lên nhau. Phân cấp │
│                                   │ 3 tầng DIM chuẩn cách nhau >= 800mm.    │
│                                   │ Không để đường gióng cắt qua số DIM.    │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 5. ĐỘ THOÁNG & THẨM MỸ BẢN VẼ     │ Bản vẽ phải mạch lạc, phân lớp layer rõ │
│                                   │ ràng, dễ đọc cho kỹ sư & công nhân.     │
└───────────────────────────────────┴─────────────────────────────────────────┘
```

---

## 📋 QUY TRÌNH LÀM VIỆC TIÊU CHUẨN (SOP) & BỘ QUY CHUẨN TRƯỚC KHI VẼ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               BẢNG THÔNG SỐ CÔNG THÁI HỌC & KÍCH THƯỚC TỐI THIỂU            │
├───────────────────────┬───────────────────────────────┬─────────────────────┤
│ HẠNG MỤC KHÔNG GIAN   │ KÍCH THƯỚC THÔNG THỦY TỐI THIỂU│ TIÊU CHUẨN THAM CHIẾU│
├───────────────────────┼───────────────────────────────┼─────────────────────┤
│ 1. Hành lang chính    │ Rộng >= 1100mm (phụ >= 900mm) │ Neufert & QCVN 04   │
│ 2. Cầu thang bộ       │ Vế thang >= 900mm; Chiếu nghỉ │ h = H/N (150-175mm) │
│                       │ >= 900mm; b = 250mm           │ b_hoàn thiện = 270mm│
│ 3. Lan can an toàn    │ Cao >= 900mm (vế), >= 1100mm  │ Khe hở nan đứng     │
│                       │ (thông tầng); Nan đứng <= 100mm│ an toàn trẻ em <=100│
│ 4. Phòng Khách        │ Diện tích >= 16m2; Rộng >=3.6m│ Cự ly xem TV >= 2.5m│
│ 5. Bếp & Phòng Ăn     │ Diện tích >= 12m2; Lối đi bếp │ Tam giác công năng  │
│                       │ >= 1000..1200mm; Bàn-tường 800│ Chu vi 4.0 - 7.5m   │
│ 6. Phòng Ngủ Master   │ Diện tích >= 14m2; Rộng >=3.3m│ Hở 2 bên giường 700 │
│ 7. Phòng Ngủ Đơn/Con  │ Diện tích >= 9m2; Rộng >= 2.7m│ Kê giường 1.2 - 1.4m│
│ 8. Vệ Sinh Tiêu Chuẩn │ Diện tích >= 3.2m2; Rộng >=1.4m│ Bệt hở trước >=600mm│
│                       │ Khoang tắm đứng >= 900x900mm  │ Hạ cốt sàn 30-50mm  │
│ 9. Giếng trời / Thông │ Nhà sâu >= 12m: Bắt buộc có ô │ Hiệu ứng ống khói   │
│    tầng lấy sáng      │ thang/giếng trời >= 5% sàn    │ Stack Effect        │
│ 10. Gara ô tô         │ Rộng >= 3.0m x Dài >= 5.5m    │ Độ dốc ram <= 15%   │
└───────────────────────┴───────────────────────────────┴─────────────────────┘
```

### 🏛️ 1. QUY TRÌNH THIẾT KẾ MỚI (5 BƯỚC)
1. **Bước 1: Nạp Nhiệm Vụ Thiết Kế**: KTS cung cấp kích thước đất, số tầng, danh sách phòng, sở thích/phong cách, ảnh tham khảo.
2. **Bước 2: Phân Tích Quy Chuẩn & Đề Xuất Bố Trí**: AI gọi `cad_tra_cuu_quy_chuan`, đối chiếu quy chuẩn, lập mô tả chi tiết phương án phân chia không gian, giao thông, giếng trời, cầu thang. **AI DỪNG LẠI CHỜ KTS CHỐT** trước khi vẽ.
3. **Bước 3: Triển Khai Vẽ Trực Tiếp**: Sau khi KTS đồng ý chốt, AI gọi `cad_ve_moi` vẽ trực tiếp lên AutoCAD (tuân thủ nghiêm ngặt nguyên tắc Không Chồng Đè).
4. **Bước 4: Tự Kiểm Tra & Sửa Lỗi**: AI tự động chạy `cad_kiem_tra` (action: `audit_full_plan`) kiểm tra kích thước thông thủy, quét sạch các lỗi chồng đè đồ đạc, chữ viết hay đường DIM.
5. **Bước 5: Báo Cáo Hoàn Thành**: Thông báo diện tích m2 chi tiết từng phòng cho KTS nghiệm thu.

---

### 🔧 2. QUY TRÌNH CHỈNH SỬA / HIỆU CHỈNH (4 BƯỚC)
1. **Bước 1: Tiếp Nhận Phản Hồi**: KTS kiểm tra bản vẽ trên AutoCAD và đưa ra yêu cầu (ví dụ: *"Kéo phòng khách rộng thêm 500mm"*).
2. **Bước 2: Thực Hiện Chỉnh Sửa**: AI gọi `cad_chinh_sua` để `STRETCH`, `MOVE`, `MIRROR` trực tiếp trên AutoCAD.
3. **Bước 3: Tự Kiểm Tra Lại**: AI gọi `cad_kiem_tra` đảm bảo việc nới rộng phòng này không làm phòng bên cạnh bị bóp hẹp dưới chuẩn và không gây đè nét lên thiết bị.
4. **Bước 4: Báo Cáo Hoàn Thành**: Zoom bản vẽ vào vị trí vừa sửa và thông báo kích thước mới cho KTS.

---

## 🏛️ HỘI ĐỒNG KIẾN TRÚC ĐA TÁC TỬ (MULTI-AGENT ARCHITECTURE)

Hệ thống được vận hành bởi **5 Chuyên Gia AI Chuyên Môn Hóa** với cơ chế tranh luận & phản biện độc lập:
1. **`KTS_Concept` (Ý Tưởng & Phân Bổ Không Gian)**: Tổ chức dây chuyền công năng, vi khí hậu, hướng gió & view cảnh quan.
2. **`KTS_Inspector_QC` (Phản Biện & Thẩm Định Độc Lập)**: "Vạch lá tìm sâu", kiểm tra đồ thị giao thông (chống bít lối đi), công thái học Neufert, QCVN 04, zero-overlap.
3. **`KySu_KetCau_MEP` (Kết Cấu & Kỹ Thuật Công Trình)**: Tối ưu lưới cột chịu lực (bỏ cột thừa), trục đứng cấp thoát nước.
4. **`HoaVien_CAD_Operator` (Họa Viên CAD Trưởng)**: Quản trị Layer, Block, DIM 3 tầng, điều khiển AutoCAD theo thời gian thực.
5. **`HoiDong_KienTruc` (Chủ Trì & Điều Phối)**: Chạy vòng lặp phản biện (Debate Loops), tối ưu hóa đạt $\ge 9.5/10$ điểm trước khi trình KTS duyệt.

---

## 🏛️ TRỌN BỘ 9 LỆNH NGHIỆP VỤ TIẾNG VIỆT (KHÔNG DẤU)

```
                  ┌─────────────────────────────────────────────────────────────┐
                  │            HỘI ĐỒNG AI ĐIỀU KHIỂN AUTOCAD TRỰC TIẾP         │
                  └──────────────┬───────────────────────────────┬──────────────┘
                                 │                               │
            GIAI ĐOẠN PHẢN BIỆN & THIẾT KẾ          GIAI ĐOẠN HỒ SƠ, DỰ TOÁN & IN ẤN
            ┌────────────────────────────┐          ┌────────────────────────────┐
            │ 0. 🏛️ cad_hop_phuong_an    │          │ 3. 📐 cad_hoan_thien_ho_so │
            │ (Hội đồng AI họp phản biện)│          │ (Dàn trang động theo TKTC) │
            │                            │          │                            │
            │ 1. ✍️ cad_ve_moi           │          │ 4. 📊 cad_du_toan          │
            │ (Vẽ mới không gian/tường)  │          │ (Bóc dự toán chi tiết Excel│
            │                            │          │                            │
            │ 2. 🔧 cad_chinh_sua        │          │ 7. 🖨️ cad_in_pdf           │
            │ (Sửa, dịch tường, đổi cửa) │          │ (In PDF đen trắng nét chuẩn│
            │                            │          │                            │
            │ 8. 📚 cad_tra_cuu_quy_chuan│          │ 5. 🔍 cad_kiem_tra (Đo/lỗi)│
            │ (Tra cứu quy chuẩn tức thì)│          │ 6. ⚡ cad_gui_lenh (Lệnh CAD│
            └────────────────────────────┘          └────────────────────────────┘
```

---

### 1️⃣ `cad_ve_moi` — Vẽ Mặt Bằng Kiến Trúc Mới
Vẽ trực tiếp mặt bằng lên không gian Model của AutoCAD theo đúng phân lớp layer chuẩn (`KT_TUONG_220`, `KT_TUONG_110`, `KT_CUA_DI`, `KT_THANG`, `KT_NOITHAT`), định vị nội thất và text không chồng đè.
* **Ví dụ ra lệnh**:
  > *"Vẽ mặt bằng nhà phố 5x15m gồm sân trước 2.5m, phòng khách 4.5m, thang 2.5m, bếp 4m, WC và sân sau 1.5m, có bố trí nội thất cơ bản."*

### 2️⃣ `cad_chinh_sua` — Sửa Đổi & Di Dời Linh Hoạt
Hiệu chỉnh, di dời mảng tường, co giãn kích thước phòng (`STRETCH`), đảo chiều mở cánh cửa (`MIRROR`), đổi layer trực tiếp trên màn hình.
* **Ví dụ ra lệnh**:
  > *"Kéo rộng phòng khách lùi về phía sau thêm 500mm và đổi cánh cửa phòng ngủ mở vào trong tường."*

### 3️⃣ `cad_hoan_thien_ho_so` — Hoàn Thiện Hồ Sơ Thi Công (Phân Trang Động & Chuẩn Thi Công)
Hệ thống **TỰ ĐỘNG PHÂN TRANG THEO KHỐI LƯỢNG THỰC TẾ** (không khống chế cứng số lượng trang A3 để đảm bảo bản vẽ in ra luôn rõ nét ở tỷ lệ kỹ thuật):

* **Kích thước Cầu thang chuẩn thi công (`KT-09`)**:
  - Chiều cao cổ bậc tính động: $h = \frac{H_{\text{tầng}}}{N_{\text{cổ bậc}}}$ (Ví dụ: Tầng cao 3.6m có 21 bậc $\rightarrow h = 171.4\text{mm}$; Tầng 3.9m có 23 bậc $\rightarrow h = 169.5\text{mm}$; Tầng 4.2m có 25 bậc $\rightarrow h = 168.0\text{mm}$).
  - Bề rộng mặt bậc xây thô chuẩn cố định: $b = 250\text{mm}$ (mặt bậc hoàn thiện ốp gỗ/đá là $270\text{mm}$ với mũi bậc chìa $20\text{mm}$ bo tròn R10).
* **Phân trang động Chi tiết cửa (`KT-11.01`, `KT-11.02`...)**:
  - Mỗi tờ A3 chỉ chứa tối đa 3-4 bộ cửa để đảm bảo tỷ lệ $1/25$ đọc rõ nét. Nếu công trình có 12 loại cửa, hệ thống tự động tách thành 4 tờ A3 riêng biệt.
* **Hệ thống các nhóm bản vẽ thi công**:
  - **Nhóm Mặt bằng**: `KT-01` (Tường xây), `KT-02` (Ốp lát sàn & mốc lát, độ dốc), `KT-03` (Bố trí nội thất & bảng thống kê), `KT-04` (Định vị cửa & bảng bậu/lanh-tô).
  - **Nhóm Mặt đứng & Mặt cắt**: `KT-05` (Mặt đứng chính công trình kèm vật liệu), `KT-06` (Mặt cắt dọc 1-1 qua thang).
  - **Nhóm Trần & Mái**: `KT-07` (Trần thạch cao giật cấp & đèn LED), `KT-08` (Mặt bằng mái & thoát nước sê-nô).
  - **Nhóm Chi tiết chuyên sâu**: `KT-09` (Chi tiết thang $h=H/N$, $b=250/270\text{mm}$), `KT-10` (Chi tiết WC trích 1/25 & 4 vách), `KT-11` (Chi tiết cửa phân trang động).

### 4️⃣ `cad_du_toan` — Bóc Tách Dự Toán Thi Công Chi Tiết (BOQ)
Tính toán khối lượng toàn diện theo định mức xây dựng Việt Nam và xuất file **Excel / CSV**:
- Bê tông móng, cột, dầm, sàn ($m^3$), ván khuôn ($m^2$), cốt thép (Tấn).
- Xây tường bao gạch ống 220 ($m^3$) & tường ngăn 110 ($m^2$) đã trừ diện tích cửa.
- Trát tường trong/ngoài ($m^2$), ốp lát gạch nền/WC ($m^2$), sơn bả 3 lớp ($m^2$), trần thạch cao ($m^2$), hệ thống cửa ($m^2$).
- Thiết bị điện chiếu sáng/ổ cắm, thiết bị vệ sinh cấp thoát nước.
* **Ví dụ ra lệnh**:
  > *"Lập bảng dự toán chi tiết công trình 2 tầng 5x15m cao 3.6m xuất ra file Excel du_toan.csv"*

### 5️⃣ `cad_kiem_tra` — Rà Soát Toàn Bộ Mặt Bằng, Chống Chồng Đè & Dọn Rác
Rà soát toàn diện mặt bằng (`audit_full_plan`) đối chiếu với toàn bộ tiêu chuẩn công thái học kiến trúc, quét sạch lỗi chồng đè đồ đạc/tường/DIM và chạy lệnh Audit / Purge dọn sạch file rác.
* **Ví dụ ra lệnh**:
  > *"Kiểm tra toàn bộ mặt bằng xem có phòng nào bị hẹp dưới chuẩn hoặc bị đè nét không và dọn rác bản vẽ."*

### 6️⃣ `cad_gui_lenh` — Gửi Lệnh AutoCAD Gốc
Gửi trực tiếp các lệnh AutoCAD như `_.ZOOM _E`, `-PURGE ALL * N`, `_.REGENALL`.

### 7️⃣ `cad_in_pdf` — In & Xuất Hồ Sơ PDF Chuẩn Nét Kỹ Thuật
In trực tiếp từ AutoCAD ra file **PDF A3/A2** với phân cấp độ dày nét chuẩn (`monochrome.ctb` in đen trắng, tường/cột $0.40\text{mm}$, nét thấy $0.20\text{mm}$, dim/trục $0.13\text{mm}$, hatch $0.09\text{mm}$):
- **In hàng loạt (`batch_all`)**: In tự động toàn bộ các trang bản vẽ đã sinh ra file PDF chuẩn A3 trong thư mục chỉ định.
- **In bản vẽ đơn (`single_sheet`)**: In riêng 1 bản vẽ theo mã hiệu (ví dụ `KT-01.01`, `KT-05`, `KT-09`, `KT-11.01`).

### 8️⃣ `cad_tra_cuu_quy_chuan` — Tra Cứu Quy Chuẩn & Công Thái Học Tức Thì
Trích xuất tức thì hướng dẫn chi tiết từ kho 7 chuyên đề kiến trúc được đóng gói trực tiếp trong mã nguồn:
- Tra cứu theo phòng (`action: 'get_room'`, `query: 'bep'`): Lấy kích thước tam giác công năng, cự ly lối đi.
- Tra cứu từ khóa (`action: 'search'`, `query: 'quy tắc 100mm'`): Tìm kiếm mọi vị trí đề cập trong quy chuẩn.
- Tra cứu chuyên đề (`action: 'get_topic'`, `query: 'cau-thang-va-hanh-lang'`): Lấy trọn vẹn văn bản hướng dẫn.
* **Ví dụ ra lệnh**:
  > *"Tra cứu tiêu chuẩn thiết kế phòng tắm vệ sinh 3 khu"* hoặc *"Tìm quy chuẩn khoảng cách nan lan can an toàn trẻ em"*

---

## 📊 TRẠNG THÁI HIỆN TẠI & ĐỊNH HƯỚNG PHÁT TRIỂN TIẾP THEO

### ✅ NHỮNG NỘI DUNG ĐÃ HOÀN THÀNH (Tính đến hiện tại):
1. **Kiến trúc DXF-First Architecture (Platform Agnostic)**: Chuyển đổi hoàn toàn từ "Live-Scripting" sang sinh file `.dxf` bằng `ezdxf` chạy ngầm. AutoCAD giờ chỉ đóng vai trò "Trình Đọc Bản Vẽ", loại bỏ 100% rủi ro lỗi đánh máy do bộ gõ tiếng Việt (Unikey/Telex) trên cả macOS và Windows.
2. **Kiểm soát va chạm hình học (Zero-Overlap)**: Bổ sung module `autocad_ai/core/geometry.py` với sức mạnh từ thư viện `shapely` để tự động kiểm tra và đảm bảo không có đồ nội thất hay mảng tường nào đè lên nhau.
3. **Kiến trúc MCP Server Đa Nền Tảng**: Hỗ trợ xuất DXF và tự động mở AutoCAD ngầm định trên macOS (`open`) và Windows (`os.startfile`).
4. **Trọn bộ 8 Lệnh Nghiệp Vụ Tiếng Việt**: `cad_ve_moi`, `cad_chinh_sua`, `cad_hoan_thien_ho_so`, `cad_du_toan`, `cad_kiem_tra`, `cad_gui_lenh`, `cad_in_pdf`, `cad_tra_cuu_quy_chuan`.
5. **Đóng gói Thư viện Quy chuẩn Kiến trúc**: Tích hợp toàn bộ kho tri thức `architecture-reference-library` trực tiếp vào `autocad_ai/knowledge/`.
6. **Bộ 2 Quy Trình SOP Tiêu Chuẩn**: Thiết kế mới 5 bước (có bước KTS duyệt chốt trước khi vẽ) và Chỉnh sửa 4 bước.
7. **Động hóa Hồ sơ & Cầu thang**: Cổ bậc thang $h=H/N$, mặt bậc $b=250/270\text{mm}$, phân trang động cửa tối đa 3-4 bộ/A3.
8. **Xuất PDF tĩnh (Preview) & Dự toán Chi tiết**: Render PNG tĩnh từ DXF cho MCP xem trước, bóc dự toán xuất file Excel/CSV.

---

### ⏳ NỘI DUNG CHƯA LÀM & ĐỊNH HƯỚNG BỔ SUNG TIẾP THEO:
1. **Chuẩn Hóa Bộ Template CAD (`.dwt`) & Thư Viện Block Riêng (ƯU TIÊN TIẾP THEO)**:
   - Khi KTS cung cấp các file mẫu `.dwg` / `.dwt` của văn phòng, hệ thống sẽ tích hợp để chèn các Block thực tế (Cửa nhôm kính Xingfa, Cửa gỗ Lim, Bệt Inax/Toto, Sofa góc chữ L, Khung tên riêng của công ty) thay vì vẽ nét vector hình học cơ bản.
2. **Triển Khai Bản Vẽ Tầng 2, Tầng 3 & Mái**:
   - Mở rộng logic `drawer.py` để hỗ trợ xếp chồng các bản vẽ tầng, kế thừa trục cột và tim tường từ Tầng 1.
3. **Lệnh Chèn Block Chuyên Nghiệp (`cad_chen_block`)**:
   - Tự động gọi chèn Block và gán thuộc tính Attribute cho Block cửa, thiết bị nội thất.
4. **Bảng Thống Kê Động Liên Kết 2 Chiều (Data Extraction)**:
   - Trích xuất bảng thống kê cửa trực tiếp từ Block Attribute trong AutoCAD và xuất ra Excel.

---

## 🔌 CẤU HÌNH VÀO AI CLIENT

### Antigravity / Claude Desktop / Cursor / VS Code:
Thêm vào file cấu hình MCP (`~/.gemini/config/mcp_config.json` hoặc `claude_desktop_config.json`):

> **Lưu ý:** Nếu bạn dùng lệnh cài đặt 1-chạm (`install-mac.sh` / `install-win.ps1`), file config sẽ được ghi tự động. Chỉ cần cấu hình thủ công nếu bạn muốn tùy chỉnh.

#### Trên macOS:
```json
{
  "mcpServers": {
    "autocad-ai": {
      "command": "/đường/dẫn/tới/autocad-ai-mcp/.venv/bin/python",
      "args": ["-m", "autocad_ai.servers.mac_server"]
    }
  }
}
```
*(Thay `/đường/dẫn/tới/autocad-ai-mcp/` bằng thư mục thực tế trên máy bạn)*

#### Trên Windows:
```json
{
  "mcpServers": {
    "autocad-ai": {
      "command": "C:\\đường\\dẫn\\tới\\autocad-ai-mcp\\.venv\\Scripts\\python.exe",
      "args": ["-m", "autocad_ai.servers.win_server"]
    }
  }
}
```
*(Thay `C:\đường\dẫn\tới\autocad-ai-mcp\` bằng thư mục thực tế trên máy bạn)*

---

## ⚠️ CẢNH BÁO BẢO MẬT

Module `autocad_mcp` (DXF engine offline) có chức năng `execute_ezdxf_script` cho phép AI viết và thực thi script Python tùy ý thông qua `exec()`. Đây là **theo thiết kế** (by design) để cho phép vẽ các hình dạng phức tạp, nhưng có rủi ro bảo mật tương đương với các MCP server có tính năng chạy code. Nếu triển khai trong môi trường chia sẻ, hãy cân nhắc giới hạn quyền truy cập thư mục làm việc.
```
