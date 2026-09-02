"""AutoCAD AI MCP Server - Windows Edition (COM ActiveX)."""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

import os
from autocad_ai.core.drawer import draw_floor_plan_to_dxf
from autocad_ai.core.modifier import build_modify_commands
from autocad_ai.core.finalizer import build_finalized_sheets_commands
from autocad_ai.core.estimator import calculate_detailed_construction_boq
from autocad_ai.core.inspector import check_room_clear_dimensions, audit_full_floor_plan, build_inspection_commands
from autocad_ai.core.plotter import build_plot_single_sheet_commands, build_batch_plot_commands
from autocad_ai.drivers.win_driver import dispatch_to_autocad_win, is_windows, open_dxf_in_autocad_win
from autocad_mcp.services.dxf_renderer import export_to_png

SERVER_INSTRUCTIONS = """AutoCAD AI Professional Architect Suite (Windows COM).

DANH SÁCH 8 LỆNH NGHIỆP VỤ TIẾNG VIỆT (KHÔNG DẤU):
1. cad_ve_moi: Vẽ mới mặt bằng kiến trúc phân lớp layer chuẩn.
2. cad_chinh_sua: Chỉnh sửa, dịch tường, co giãn kích thước, đổi cửa trực tiếp.
3. cad_hoan_thien_ho_so: Dàn trang & hoàn thiện trọn bộ 11+ bản vẽ thi công TKTC.
4. cad_du_toan: Bóc tách dự toán chi tiết công trình ra file Excel / CSV.
5. cad_kiem_tra: Rà soát toàn diện quy chuẩn mặt bằng, đo đạc thông thủy & dọn rác.
6. cad_gui_lenh: Gửi trực tiếp lệnh AutoCAD gốc (ZOOM, PURGE, REGENALL).
7. cad_in_pdf: In ấn & xuất hồ sơ PDF A3 đen trắng chuẩn nét kỹ thuật.
8. cad_tra_cuu_quy_chuan: Tra cứu tức thì công thái học & quy chuẩn kiến trúc từ thư viện mã nguồn.

RÀNG BUỘC BẮT BUỘC: BẢN VẼ SẠCH SẼ - KHÔNG CHỒNG ĐÈ (ÁP DỤNG KHI VẼ & KHI KIỂM TRA):
- CẤM đồ nội thất đè vào tường hoặc lấn qua mảng tường 110/220 (trừ hộc tủ âm tường).
- CẤM tường đè lên đồ nội thất, thiết bị vệ sinh hoặc bếp.
- CẤM chữ / ghi chú / cao độ đè lên nhau, đè lên nét vẽ hoặc đè lên hatch.
- CẤM đường kích thước DIM đè lên nhau (phân cấp 3 tầng DIM rõ ràng cách nhau >= 800mm).
- Bản vẽ phải luôn sạch sẽ, mạch lạc, dễ nhìn và thoáng đãng.

TUÂN THỦ 2 QUY TRÌNH CHUẨN CỦA KIẾN TRÚC SƯ:
🏛️ QUY TRÌNH 1: THIẾT KẾ MỚI (5 BƯỚC)
1. Bước 1: Tiếp nhận diện tích, công năng, sở thích, ảnh mẫu.
2. Bước 2: Đối chiếu quy chuẩn & Đề xuất phương án. DỪNG LẠI CHỜ KTS CHỐT PHƯƠNG ÁN trước khi vẽ.
3. Bước 3: Gọi 'cad_ve_moi' vẽ trực tiếp lên AutoCAD theo phương án đã chốt (đảm bảo không chồng đè).
4. Bước 4: Gọi 'cad_kiem_tra' (action='audit_full_plan') tự kiểm tra toàn diện thông thủy & tự sửa nếu có lệch/đè nét.
5. Bước 5: Báo cáo hoàn thành bảng diện tích m2 và thông số cho KTS.

🔧 QUY TRÌNH 2: CHỈNH SỬA / HIỆU CHỈNH (4 BƯỚC)
1. Bước 1: Tiếp nhận yêu cầu chỉnh sửa từ KTS.
2. Bước 2: Gọi 'cad_chinh_sua' để Stretch, Move, Mirror, Rotate trực tiếp trên AutoCAD.
3. Bước 3: Rà soát không gian ảnh hưởng, đảm bảo không làm phòng lân cận bị hẹp dưới chuẩn và không gây chồng đè.
4. Bước 4: Zoom đến vị trí sửa và thông báo kích thước mới cho KTS.
"""

mcp = FastMCP(
    name="autocad-ai-win",
    instructions=SERVER_INSTRUCTIONS,
)


# ============================================================================
# 1. VẼ MỚI (cad_ve_moi)
# ============================================================================


@mcp.tool()
def cad_ve_moi(
    frontage_width_mm: float,
    depth_length_mm: float,
    rooms: List[Dict[str, Any]],
    wall_ext_mm: float = 220.0,
    wall_int_mm: float = 110.0,
    include_furniture: bool = True,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
) -> Dict[str, Any]:
    """
    1. VẼ MẶT BẰNG MỚI (cad_ve_moi):
    Vẽ trực tiếp mặt bằng kiến trúc mới lên AutoCAD Windows COM theo đúng phân lớp layer chuẩn:
    - KT_TUONG_220 (Tường bao 220, Cột)
    - KT_TUONG_110 (Tường ngăn 110)
    - KT_CUA_DI (Cửa đi chính, cửa phòng)
    - KT_CUA_SO (Cửa sổ lấy sáng, lấy gió)
    - KT_THANG (Bậc thang, tim thang)
    - KT_NOITHAT (Sofa, bàn ăn, bếp, bệt, lavabo)
    """
    dxf_path = os.path.expanduser("~\\.autocad_ai\\mat_bang_moi.dxf")
    os.makedirs(os.path.dirname(dxf_path), exist_ok=True)
    
    # 1. Tạo bản vẽ DXF
    draw_floor_plan_to_dxf(
        filepath=dxf_path,
        width_mm=frontage_width_mm,
        length_mm=depth_length_mm,
        rooms=rooms,
        wall_ext_mm=wall_ext_mm,
        wall_int_mm=wall_int_mm,
        include_furniture=include_furniture,
        origin_x=origin_x,
        origin_y=origin_y,
    )
    
    # 2. Render ảnh PNG tĩnh từ DXF để user xem trước
    try:
        png_res = export_to_png(dxf_path, dpi=150)
        png_path = png_res.get("output_path", "")
    except Exception as e:
        png_path = f"Lỗi tạo PNG: {str(e)}"

    # 3. Mở file DXF bằng AutoCAD trực tiếp (chạy ngầm)
    open_res = open_dxf_in_autocad_win(dxf_path)
    open_res["preview_png"] = png_path
    
    return open_res


# ============================================================================
# 2. CHỈNH SỬA / HIỆU CHỈNH (cad_chinh_sua)
# ============================================================================


@mcp.tool()
def cad_chinh_sua(
    action: str,
    target: str = "wall",
    dx: float = 0.0,
    dy: float = 0.0,
    window_p1: Optional[List[float]] = None,
    window_p2: Optional[List[float]] = None,
    new_layer: Optional[str] = None,
    rotation_deg: float = 0.0,
) -> Dict[str, Any]:
    """
    2. CHỈNH SỬA BẢN VẼ (cad_chinh_sua):
    Thực hiện các thao tác sửa đổi, co giãn, dịch chuyển mảng tường và cửa trực tiếp trên AutoCAD Windows COM:
    - action:
        * 'stretch_room': Co giãn phòng (dx, dy theo mm)
        * 'move_wall': Dời tường (dx, dy theo mm)
        * 'mirror_door': Đảo chiều mở cánh cửa
        * 'rotate_object': Xoay đối tượng (rotation_deg)
        * 'change_layer': Đổi layer đối tượng sang new_layer
        * 'delete_object': Xóa đối tượng trong vùng chọn
    """
    # Map action names from server conventions → modifier conventions
    ACTION_MAP = {
        "stretch_room": "stretch",
        "move_wall": "move",
        "mirror_door": "mirror",
        "rotate_object": "mirror",
        "change_layer": "change_layer",
        "delete_object": "delete",
        "move": "move",
        "stretch": "stretch",
        "resize_room": "resize_room",
        "change_door_swing": "change_door_swing",
        "flip_door": "flip_door",
        "mirror": "mirror",
        "delete": "delete",
        "erase": "erase",
    }
    mapped_action = ACTION_MAP.get(action.lower().strip(), action)

    parameters = {
        "dx": dx,
        "dy": dy,
        "base_point": window_p1 or [0, 0],
        "crossing_corner1": window_p1 or [0, 0],
        "crossing_corner2": window_p2 or [1000, 1000],
        "axis_p1": window_p1 or [0, 0],
        "axis_p2": window_p2 or [0, 1000],
        "layer": new_layer or "0",
        "rotation_deg": rotation_deg,
        "delete_original": True,
    }

    cmds = build_modify_commands(
        action=mapped_action,
        target_description=target,
        parameters=parameters,
    )
    return dispatch_to_autocad_win(cmds)


# ============================================================================
# 3. HOÀN THIỆN HỒ SƠ THI CÔNG (cad_hoan_thien_ho_so)
# ============================================================================


@mcp.tool()
def cad_hoan_thien_ho_so(
    sheet_type: str = "full_project_set",
    frontage_width_mm: float = 5000.0,
    depth_length_mm: float = 15000.0,
    rooms: Optional[List[Dict[str, Any]]] = None,
    floor_height_mm: float = 3600.0,
    num_floors: int = 2,
    num_risers: int = 21,
    doors: Optional[List[Dict[str, Any]]] = None,
    wc_count: int = 2,
    origin_x: float = 0.0,
    origin_y: float = 0.0,
    project_name: str = "Nhà Phố Dân Dụng",
) -> Dict[str, Any]:
    """
    3. HOÀN THIỆN HỒ SƠ THI CÔNG TKTC (cad_hoan_thien_ho_so):
    Tự động phân trang động & xuất trọn bộ bản vẽ thi công chuyên nghiệp lồng sẵn khung tên A3:
    - sheet_type:
        * 'full_project_set': Xuất trọn bộ 11+ bản vẽ kỹ thuật.
        * 'all_floor_plans': Bộ 4 mặt bằng (KT-01 Tường xây, KT-02 Lát sàn, KT-03 Nội thất, KT-04 Định vị cửa).
        * 'elevation': KT-05 Mặt đứng chính kèm vật liệu & cao độ.
        * 'section': KT-06 Mặt cắt dọc 1-1 qua thang.
        * 'ceiling_lighting': KT-07 Mặt bằng trần thạch cao & đèn chiếu sáng.
        * 'roof_drainage': KT-08 Mặt bằng mái & thoát nước sê-nô.
        * 'stair_detail': KT-09 Chi tiết thang chuẩn thi công (b=250/270mm, h=H/N).
        * 'wc_detail': KT-10 Chi tiết WC trích 1/25 & 4 vách ốp lát.
        * 'door_detail': KT-11 Chi tiết cấu tạo cửa phân trang động (tối đa 3-4 cửa/A3).
    """
    cmds = build_finalized_sheets_commands(
        sheet_type=sheet_type,
        width_mm=frontage_width_mm,
        depth_length_mm=depth_length_mm,
        rooms=rooms,
        floor_height_mm=floor_height_mm,
        num_floors=num_floors,
        num_risers=num_risers,
        doors=doors,
        wc_count=wc_count,
        origin_x=origin_x,
        origin_y=origin_y,
        project_name=project_name,
    )
    return dispatch_to_autocad_win(cmds)


# ============================================================================
# 4. BÓC TÁCH DỰ TOÁN CHI TIẾT (cad_du_toan)
# ============================================================================


@mcp.tool()
def cad_du_toan(
    frontage_width_m: float,
    depth_length_m: float,
    num_floors: int = 2,
    floor_height_m: float = 3.6,
    num_bedrooms: int = 3,
    num_bathrooms: int = 2,
    output_csv_file: Optional[str] = None,
) -> Dict[str, Any]:
    """
    4. LẬP BẢNG DỰ TOÁN THI CÔNG CHI TIẾT (cad_du_toan):
    Bóc tách khối lượng toàn diện (Bê tông, ván khuôn, cốt thép, xây tường 220/110 trừ cửa, trát trong/ngoài, ốp lát, sơn bả, trần thạch cao, cửa, MEP) theo định mức xây dựng Việt Nam và xuất file CSV/Excel.
    """
    return calculate_detailed_construction_boq(
        frontage_w_m=frontage_width_m,
        depth_l_m=depth_length_m,
        num_floors=num_floors,
        floor_height_m=floor_height_m,
        num_bedrooms=num_bedrooms,
        num_bathrooms=num_bathrooms,
        output_csv_path=output_csv_file,
    )


# ============================================================================
# 5. KIỂM TRA & RÀ SOÁT QUY CHUẨN (cad_kiem_tra)
# ============================================================================


@mcp.tool()
def cad_kiem_tra(
    length_mm: Optional[float] = None,
    width_mm: Optional[float] = None,
    room_type: str = "living",
    action: str = "check_standard",
    rooms: Optional[List[Dict[str, Any]]] = None,
    frontage_width_mm: float = 5000.0,
    depth_length_mm: float = 15000.0,
    floor_height_mm: float = 3600.0,
    num_risers: int = 21,
) -> Dict[str, Any]:
    """
    5. KIỂM TRA & RÀ SOÁT QUY CHUẨN KIẾN TRÚC (cad_kiem_tra):
    Rà soát toàn diện phương án theo bộ tiêu chuẩn Neufert & Quy chuẩn Xây Dựng VN (architecture-reference-library).
    - action:
        * 'check_standard': Kiểm tra kích thước thông thủy 1 phòng (diện tích, chiều hẹp).
        * 'audit_full_plan': Rà soát toàn bộ mặt bằng (hành lang, giếng trời, tam giác bếp, cầu thang, an toàn trẻ em).
        * 'audit_purge': Thực hiện lệnh AUDIT và PURGE dọn sạch rác bản vẽ trên AutoCAD.
    """
    if action == "audit_full_plan" and rooms:
        res = audit_full_floor_plan(
            width_mm=frontage_width_mm,
            length_mm=depth_length_mm,
            rooms=rooms,
            floor_height_mm=floor_height_mm,
            num_risers=num_risers,
        )
    else:
        l = length_mm or depth_length_mm
        w = width_mm or frontage_width_mm
        res = check_room_clear_dimensions(l, w, room_type)

    if action == "audit_purge":
        cmds = build_inspection_commands("audit_purge")
        dispatch_to_autocad_win(cmds)
        res["cad_clean_status"] = "Executed AUDIT & PURGE on AutoCAD"
    return res


# ============================================================================
# 6. GỬI LỆNH AUTOCAD GỐC (cad_gui_lenh)
# ============================================================================


@mcp.tool()
def cad_gui_lenh(commands: List[str]) -> Dict[str, Any]:
    """
    6. GỬI LỆNH AUTOCAD TRỰC TIẾP (cad_gui_lenh):
    Gửi bất kỳ chuỗi lệnh AutoCAD gốc nào vào cửa sổ AutoCAD Windows đang mở.
    Ví dụ: ['_.ZOOM _E', '-PURGE ALL * N', '_.REGENALL']
    """
    return dispatch_to_autocad_win(commands)


# ============================================================================
# 7. IN ẤN & XUẤT PDF CHUẨN NÉT (cad_in_pdf)
# ============================================================================


@mcp.tool()
def cad_in_pdf(
    plot_scope: str = "batch_all",
    sheet_code: str = "KT-01",
    output_pdf_file: Optional[str] = None,
    output_directory: Optional[str] = None,
    project_name: str = "NHA_PHO",
    paper_size: str = "A3",
    plot_style: str = "monochrome.ctb",
    window_p1: Optional[List[float]] = None,
    window_p2: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """
    7. IN & XUẤT HỒ SƠ PDF CHUẨN KỸ THUẬT (cad_in_pdf):
    In trực tiếp từ AutoCAD ra file PDF với đầy đủ độ dày nét phân cấp và màu đen chuẩn (monochrome.ctb).
    - plot_scope:
        * 'batch_all': In hàng loạt toàn bộ các bản vẽ kỹ thuật ra các file PDF chuẩn A3 trong thư mục chỉ định.
        * 'single_sheet': In 1 bản vẽ cụ thể theo tọa độ window hoặc mã hiệu bản vẽ.
    - paper_size: 'A3' (mặc định 420x297mm), 'A2', 'A4'
    - plot_style: 'monochrome.ctb' (in đen trắng nét kỹ thuật), 'acad.ctb' (in theo màu layer)
    - output_directory: Thư mục lưu file PDF xuất ra
    """
    if plot_scope in ("batch_all", "batch", "all"):
        batch_res = build_batch_plot_commands(
            output_directory=output_directory,
            project_name=project_name,
            paper_size=paper_size,
            plot_style=plot_style,
        )
        dispatch_res = dispatch_to_autocad_win(batch_res["commands"])
        batch_res["dispatch_status"] = dispatch_res
        return batch_res
    else:
        out_pdf = output_pdf_file or f"~/Desktop/{project_name}_{sheet_code}.pdf"
        p1 = window_p1 or [-2000.0, -3000.0]
        p2 = window_p2 or [12000.0, 17000.0]
        cmds = build_plot_single_sheet_commands(
            sheet_code=sheet_code,
            window_p1=p1,
            window_p2=p2,
            output_pdf_path=out_pdf,
            paper_size=paper_size,
            plot_style=plot_style,
        )
        cmds.append("_.ZOOM _E")
        dispatch_res = dispatch_to_autocad_win(cmds)
        return {
            "status": "success",
            "sheet_code": sheet_code,
            "output_pdf": out_pdf,
            "paper_size": paper_size,
            "plot_style": plot_style,
            "dispatch_status": dispatch_res,
        }


# ============================================================================
# 8. TRA CỨU QUY CHUẨN KIẾN TRÚC (cad_tra_cuu_quy_chuan)
# ============================================================================


@mcp.tool()
def cad_tra_cuu_quy_chuan(
    action: str = "get_room",
    query: str = "living",
) -> Dict[str, Any]:
    """
    8. TRA CỨU QUY CHUẨN & HƯỚNG DẪN THIẾT KẾ (cad_tra_cuu_quy_chuan):
    Trích xuất tức thì các hướng dẫn, tiêu chuẩn công thái học & quy chuẩn kỹ thuật từ thư viện mã nguồn kiến trúc:
    - action:
        * 'get_room': Lấy hướng dẫn chi tiết cho 1 phòng ('khach', 'bep', 'wc', 'ngu', 'master', 'thang', 'gieng_troi', 'gara').
        * 'search': Tìm kiếm nhanh từ khóa (ví dụ: 'tam giác bếp', 'cổ bậc', 'quy tắc 100mm', 'độ dốc ram', 'chống thấm').
        * 'get_topic': Lấy toàn bộ chuyên đề theo tên file (ví dụ: 'cau-thang-va-hanh-lang', 'he-thong-cap-thoat-nuoc', 'ket-cau-be-tong-cot-thep').
        * 'list_all': Liệt kê toàn bộ 7 nhóm chuyên đề có trong thư viện mã nguồn.
    """
    from autocad_ai.knowledge.engine import (
        get_library_topics,
        get_full_topic_document,
        search_reference_library,
        get_room_guidelines,
    )

    if action == "list_all":
        return {"topics": get_library_topics()}
    elif action == "search":
        return {"keyword": query, "results": search_reference_library(query)}
    elif action == "get_topic":
        doc = get_full_topic_document(query)
        return doc or {"error": f"Không tìm thấy chuyên đề '{query}'"}
    else:  # get_room
        return get_room_guidelines(query)



# ============================================================================
# WORKFLOW PROMPTS (QUY TRÌNH CHUẨN)
# ============================================================================


@mcp.prompt()
def new_design_proposal(project_brief: str) -> str:
    """Quy trình 1: Hướng dẫn AI tiếp nhận nhiệm vụ thiết kế, phân tích, đề xuất phương án và chờ KTS chốt."""
    return f"""Bạn là Trợ lý Kiến Trúc Sư AI chuyên nghiệp. Hãy tuân thủ QUY TRÌNH THIẾT KẾ MỚI (5 BƯỚC) cho nhiệm vụ sau:
Nhiệm vụ thiết kế: "{project_brief}"

CÁC BƯỚC THỰC HIỆN:
1. BƯỚC 1: Phân tích kỹ diện tích khu đất (rộng x dài), số tầng, nhu cầu các phòng, phong thủy, phong cách.
2. BƯỚC 2 (QUAN TRỌNG): Tra cứu quy chuẩn ('cad_tra_cuu_quy_chuan') và lập bảng mô tả chi tiết phương án bố trí mặt bằng (phân bổ diện tích, vị trí thang, giếng trời, lối đi). DỪNG LẠI VÀ HỎI KIẾN TRÚC SƯ ĐỂ CHỐT PHƯƠNG ÁN. CHƯA ĐƯỢC VẼ KHI KTS CHƯA CHỐT!
3. BƯỚC 3: Sau khi KTS đồng ý chốt, gọi 'cad_ve_moi' vẽ trực tiếp lên AutoCAD.
4. BƯỚC 4: Tự kiểm tra lại bằng 'cad_kiem_tra' (action='audit_full_plan') và tự sửa nếu có lệch.
5. BƯỚC 5: Báo cáo hoàn thành bảng diện tích từng phòng cho KTS.
"""


@mcp.prompt()
def modify_design_request(modification_brief: str) -> str:
    """Quy trình 2: Hướng dẫn AI tiếp nhận yêu cầu chỉnh sửa từ KTS, sửa trực tiếp trên AutoCAD, tự kiểm tra và báo cáo."""
    return f"""Bạn là Trợ lý Kiến Trúc Sư AI chuyên nghiệp. Hãy tuân thủ QUY TRÌNH CHỈNH SỬA (4 BƯỚC) cho yêu cầu sau:
Yêu cầu chỉnh sửa: "{modification_brief}"

CÁC BƯỚC THỰC HIỆN:
1. BƯỚC 1: Phân tích đối tượng cần sửa và phạm vi ảnh hưởng (tường nào, phòng nào bị co giãn).
2. BƯỚC 2: Gọi 'cad_chinh_sua' để thực hiện lệnh Stretch, Move, Mirror, Rotate trực tiếp trên AutoCAD.
3. BƯỚC 3: Tự kiểm tra lại ('cad_kiem_tra') diện tích phòng mới và các không gian lân cận để đảm bảo không phát sinh xung đột.
4. BƯỚC 4: Báo cáo hoàn thành, thông báo kích thước mới và zoom đến vị trí vừa sửa cho KTS xem.
"""


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
