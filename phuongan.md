# Phương án sửa `autocad-ai-mcp` để chạy được như quảng cáo

- **Repo:** https://github.com/haianhdskt-boop/autocad-ai-mcp
- **Ngày lập:** 2026-09-02
- **Mục tiêu:** biến prototype hiện tại thành hệ thống **vận hành thật, tin cậy, kiểm thử được** — đúng như README mô tả (vẽ mặt bằng, chỉnh sửa, hoàn thiện hồ sơ, dự toán, kiểm tra chống chồng đè, in PDF).
- **Tài liệu này chỉ ĐỀ XUẤT — chưa sửa mã.** Bạn xem xét, chọn phạm vi, rồi tôi mới triển khai.

---

## 1. Chẩn đoán gốc rễ (vì sao bản hiện tại không đạt)

| # | Nguyên nhân gốc | Hệ quả |
|---|---|---|
| A | **"Gõ lệnh mù"**: sinh chuỗi text (`_.-TEXT`, `_.RECTANG`...) bắn qua `SendCommand` | Nhạy phiên bản/ngôn ngữ/kiểu chữ; tiếng Việt vỡ font; prompt lệch là sai toàn bộ |
| B | **Không đọc ngược** trạng thái từ AutoCAD sống | Sửa "mù" bằng `_P` (Previous), chọn nhầm/rỗng; "tự kiểm tra bản vẽ" là ảo |
| C | **Không có mô hình hình học thật** (chỉ vẽ rectangle rời rạc, không có cửa/cửa sổ, không phát hiện va chạm) | "Không chồng đè" chỉ là prompt + offset cứng, không kiểm chứng được |
| D | **Hồ sơ thi công = khung mẫu**, text ghi cứng | Không phải bản vẽ dùng được; `-PLOT` macro cứng dễ hỏng |
| E | **Hai codebase song song** (`autocad_mcp` DXF-offline vs `autocad_ai` live) rời rạc | Trùng lặp, phần đáng tin (ezdxf) không được suite live tận dụng |

**Kết luận:** vấn đề không nằm ở vài bug lẻ mà ở **kiến trúc**. Cần đổi mô hình thực thi.

---

## 2. Nguyên tắc kiến trúc mục tiêu

> **"Model → DXF → (tùy chọn) đồng bộ Live"**, thay cho **"LLM → chuỗi lệnh → AutoCAD"**.

Ý tưởng cốt lõi: **dựng bản vẽ bằng `ezdxf` (xác định, unicode-safe, kiểm thử được không cần AutoCAD)**; AutoCAD sống chỉ là lớp đồng bộ **tùy chọn** và dùng **COM object model** (`AddLine`, `AddLWPolyline`, `InsertBlock`, đọc `Handle`) — **không** dùng chuỗi lệnh `SendCommand`.

```
┌─────────────────────────────────────────────────────────────┐
│ L1. DOMAIN MODEL (dataclasses thuần)                         │
│     FloorPlan · Room · Wall · Door · Window · Furniture      │
├─────────────────────────────────────────────────────────────┤
│ L2. GEOMETRY & VALIDATION (shapely)                          │
│     - phát hiện va chạm THẬT (tường↔nội thất, text↔net...)   │
│     - kiểm tra thông thủy/khoảng hở theo Neufert/QCVN        │
│     → "không chồng đè" & "tự kiểm tra" trở thành THẬT        │
├─────────────────────────────────────────────────────────────┤
│ L3. DXF AUTHORING (ezdxf)                                    │
│     - entity thật + handle + layer chuẩn                     │
│     - CỬA/CỬA SỔ bằng block, MTEXT unicode, DIM thật         │
│     → xác định, unit-test không cần AutoCAD                  │
├─────────────────────────────────────────────────────────────┤
│ L4. RENDER/EXPORT (đã có sẵn dxf_renderer)                   │
│     DXF → PNG/SVG/PDF offline  → AI "nhìn thấy" & in tin cậy │
├─────────────────────────────────────────────────────────────┤
│ L5. LIVE BRIDGE — TÙY CHỌN                                   │
│     Windows: COM object model + ĐỌC NGƯỢC handle            │
│     macOS:   mở/chèn file DXF (không "gõ phím" AppleScript)  │
├─────────────────────────────────────────────────────────────┤
│ L6. EDIT theo HANDLE thật (từ đọc ngược ở L5/L3)            │
│     Move/Stretch/Rotate/Mirror/Layer đúng đối tượng          │
└─────────────────────────────────────────────────────────────┘
```

**Lợi ích lớn nhất:** phần lõi (L1–L4) chạy **không cần AutoCAD**, **kiểm thử tự động 100%**, **unicode chuẩn**, và **hợp nhất 2 package** — `autocad_mcp` (ezdxf) thành engine, `autocad_ai` thành lớp nghiệp vụ + cầu nối live.

---

## 3. Lộ trình theo giai đoạn (chọn phạm vi được)

Mỗi giai đoạn độc lập tạo giá trị; có thể dừng ở bất kỳ đâu.

### Giai đoạn 0 — Ổn định & trung thực hóa (0.5–1 ngày)
- Sửa lỗi ngữ nghĩa còn lại: `rotate_object` hiện map thành `mirror`, `rotation_deg` không dùng → thêm nhánh `_.ROTATE` thật (hoặc bỏ quảng cáo xoay).
- README ghi rõ trạng thái "thử nghiệm/khung mẫu" cho các tính năng chưa hoàn chỉnh.
- **Mục tiêu:** không còn tuyên bố sai lệch; nền sạch để refactor.

### Giai đoạn 1 — Lõi DXF-first + render/PDF offline ⭐ (ROI cao nhất, 3–5 ngày)
- Tạo L1 (domain model) + L3 (`ezdxf` authoring) cho `cad_ve_moi`: vẽ tường 220/110 thật, **có cửa/cửa sổ** (block), nội thất, MTEXT tiếng Việt chuẩn, DIM.
- Nối L4: xuất **PNG/SVG/PDF ngay từ DXF** (tận dụng `autocad_mcp/services/dxf_renderer.py`) → thay `cad_in_pdf` bằng đường in **không phụ thuộc `-PLOT`**.
- Thêm tool `cad_xem_truoc` trả PNG để AI/KTS xem kết quả.
- **Mục tiêu:** `cad_ve_moi` + in ấn **chạy tin cậy trên mọi máy, kể cả không có AutoCAD**. Đây là bước biến hệ thống thành "dùng được".

### Giai đoạn 2 — Kiểm tra hình học THẬT (2–3 ngày)
- L2 với `shapely`: phát hiện chồng đè (nội thất↔tường, text↔nét, DIM↔DIM), đo thông thủy, khoảng hở.
- `cad_kiem_tra` đọc **hình học thật từ DXF** (qua `dxf_reader`) thay vì số liệu AI tự nhập.
- Vòng lặp tự sửa: phát hiện đè → dịch/scale trong model → xuất lại.
- **Mục tiêu:** cam kết "Zero-Overlap" và "Bước 4 tự kiểm tra" trở thành thật, kiểm chứng được.

### Giai đoạn 3 — Cầu nối Live tin cậy trên Windows (3–5 ngày)
- Viết lại `win_driver` dùng **COM object model** (`ModelSpace.AddLWPolyline/AddText/InsertBlock`) thay chuỗi lệnh → hết lỗi prompt/locale/dấu.
- **Đọc ngược**: hàm liệt kê entity + `Handle` + tọa độ từ bản vẽ đang mở → trả cho AI.
- `cad_chinh_sua` chọn **đúng đối tượng theo handle** rồi Move/Stretch/Rotate/Mirror.
- **Mục tiêu:** vẽ & sửa trực tiếp trên AutoCAD Windows **đúng đối tượng, đáng tin**.

### Giai đoạn 4 — Hồ sơ thi công thật + thư viện block (5–8 ngày)
- Thay các "khung mẫu" bằng generator lấy dữ liệu **từ model thật** (mặt cắt/mặt đứng suy ra từ mặt bằng + chiều cao tầng).
- Nạp thư viện block `.dwg/.dwt` của văn phòng (cửa, thiết bị, khung tên) — chèn block thật thay vì vẽ rectangle.
- In PDF qua đối tượng `Plot` COM (hoặc tiếp tục đường DXF→PDF offline).
- **Mục tiêu:** `cad_hoan_thien_ho_so` cho ra hồ sơ dùng được, không phải stub.

### Giai đoạn 5 — Chiến lược macOS (2–3 ngày)
- Bỏ "gõ phím" AppleScript. Thay bằng: xuất DXF → mở/`-INSERT` vào bản vẽ Mac, hoặc dùng đường offline (L1–L4) là chính.
- **Mục tiêu:** Mac dùng được ổn định (dù không có COM read-back như Windows).

---

## 4. Tiêu chí nghiệm thu ("thế nào là chạy được như quảng cáo")

| Tính năng | Tiêu chí PASS (kiểm thử được) |
|---|---|
| `cad_ve_moi` | Sinh DXF mở được trong AutoCAD; có tường 220/110 + **cửa/cửa sổ** + nội thất + text tiếng Việt **không vỡ font**; PNG preview khớp |
| Zero-Overlap | `cad_kiem_tra` chạy trên DXF thật, phát hiện đúng ≥1 case đè cố ý; sau tự sửa thì báo 0 đè |
| `cad_chinh_sua` | Dịch/xoay **đúng đối tượng chỉ định** (verify qua handle/tọa độ đọc ngược), phòng lân cận không sai chuẩn |
| `cad_hoan_thien_ho_so` | Bản vẽ suy ra từ model thật (đổi số tầng/kích thước → hồ sơ đổi theo), không phải text cứng |
| `cad_in_pdf` | Ra PDF A3 đúng nét trên máy **không cần** cấu hình `DWG To PDF.pc3` thủ công |
| `cad_du_toan` | (đã đạt) khối lượng + CSV đúng |
| `cad_tra_cuu_quy_chuan` | (đã đạt) trả đúng tài liệu |
| Toàn hệ | `pytest` phủ **cả tầng tool MCP**, chạy xanh **không cần AutoCAD** cho L1–L4 |

---

## 5. Tận dụng lại & bỏ đi

**Giữ & tái dùng (đã tốt):**
- `autocad_mcp/services/dxf_reader.py`, `dxf_writer.py`, `dxf_renderer.py` → nền cho L3/L4.
- `autocad_ai/core/estimator.py` (dự toán), `knowledge/` (tra cứu) → giữ nguyên.
- `autocad_ai/core/finalizer.py` bố cục khung tên/phân trang → tái dùng phần layout.

**Viết lại:**
- `drawer.py`, `modifier.py` → chuyển từ sinh chuỗi lệnh sang dựng model + ezdxf.
- `win_driver.py`, `mac_driver.py`, `live/*bridge*` → COM object model + đọc ngược / đường DXF.
- `cad_in_pdf` → render offline hoặc Plot COM.

**Thêm mới:**
- `core/model.py` (L1), `core/geometry.py` (L2, `shapely`), `core/dxf_builder.py` (L3).
- Phụ thuộc mới: `shapely` (thêm vào `requirements.txt`/`pyproject.toml`).

---

## 6. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| COM object model khác nhau giữa AutoCAD/ZWCAD/BricsCAD | Trừu tượng hóa qua interface driver; test trên từng CAD; fallback đường DXF |
| Thiếu máy có AutoCAD để kiểm thử live | L1–L4 test 100% offline; L5–L6 kiểm thử thủ công theo checklist bạn chạy |
| Thư viện block `.dwg` của văn phòng chưa có | Giai đoạn 4 cần bạn cung cấp; trước đó dùng block hình học tạm |
| Phạm vi phình to | Làm theo giai đoạn, dừng được sau G1/G2 vẫn có sản phẩm dùng được |

---

## 7. Khuyến nghị phạm vi tối thiểu để "dùng được thật"

**Làm Giai đoạn 1 + 2** (khoảng 5–8 ngày) là đủ cho một hệ thống **thực sự chạy được**:
- Vẽ mặt bằng có cửa/nội thất + text Việt chuẩn, xuất PNG/PDF tin cậy **không cần AutoCAD**.
- Kiểm tra chống chồng đè & thông thủy **thật**.
- Dự toán + tra cứu quy chuẩn (đã có).

Live AutoCAD (G3+) là "điểm cộng" cho ai cần vẽ trực tiếp trên màn hình — làm sau khi lõi đã vững.

---

## 8. Đề xuất bước tiếp theo

Xin bạn chọn:
1. **Phạm vi:** chỉ G1+G2 (khuyến nghị), hay full G1→G5?
2. **Ưu tiên nền tảng:** DXF-offline trước (dùng mọi máy) hay Live-Windows trước (cần AutoCAD)?
3. **Có sẵn thư viện block `.dwg/.dwt` + file `.ctb`** của văn phòng để tích hợp ở G4 không?

Sau khi bạn chốt, tôi sẽ lập kế hoạch triển khai chi tiết (tách task, thứ tự file, test) và bắt đầu sửa.
