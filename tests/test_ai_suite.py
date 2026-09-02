"""Unit tests for AutoCAD AI MCP Suite."""

import os
import pytest
import tempfile
import asyncio

from autocad_ai.core.drawer import draw_floor_plan_to_dxf
from autocad_ai.core.modifier import build_modify_commands
from autocad_ai.core.finalizer import (
    build_finalized_sheets_commands,
    build_wall_construction_sheet_commands,
    build_floor_finishes_sheet_commands,
    build_furniture_layout_sheet_commands,
    build_door_schedule_sheet_commands,
)
from autocad_ai.core.estimator import calculate_detailed_construction_boq
from autocad_ai.core.inspector import check_room_clear_dimensions
from autocad_ai.servers.mac_server import mcp as mac_mcp
from autocad_ai.servers.win_server import mcp as win_mcp


def test_drawer_dxf_generation():
    """Test generating DXF floor plan."""
    rooms = [
        {"name": "Phòng Khách", "y_start": 2500, "y_end": 7000, "type": "living"},
        {"name": "Cầu Thang", "y_start": 7000, "y_end": 9500, "type": "stairs"},
    ]
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as tf:
        dxf_path = tf.name

    try:
        res_path = draw_floor_plan_to_dxf(
            filepath=dxf_path,
            width_mm=5000,
            length_mm=15000,
            rooms=rooms
        )
        assert os.path.exists(res_path)
        assert os.path.getsize(res_path) > 1000
    finally:
        if os.path.exists(dxf_path):
            os.remove(dxf_path)


def test_modifier_commands():
    """Test modification command generation."""
    move_cmds = build_modify_commands("move", "dịch tường 500mm", {"dx": 500, "dy": 0})
    assert any("_.MOVE" in c for c in move_cmds)

    mirror_cmds = build_modify_commands("flip_door", "đảo chiều cửa phòng")
    assert any("_.MIRROR" in c for c in mirror_cmds)

    stretch_cmds = build_modify_commands("stretch", "kéo dài phòng", {"dx": 300})
    assert any("_.STRETCH" in c for c in stretch_cmds)


def test_finalizer_all_11_sheets():
    """Test generating all 11 architectural construction documentation sheets."""
    rooms = [
        {"name": "PHÒNG KHÁCH", "y_start": 2500, "y_end": 7000, "type": "living"},
        {"name": "WC", "y_start": 13500, "y_end": 15000, "type": "wc"},
    ]

    # Sheet 1: KT-01 Wall construction
    s1 = build_wall_construction_sheet_commands(5000, 15000, rooms)
    assert "KT-01" in " ".join(s1)

    # Sheet 2: KT-02 Floor finishes
    s2 = build_floor_finishes_sheet_commands(5000, 15000, rooms)
    assert "KT-02" in " ".join(s2)

    # Sheet 3: KT-03 Furniture layout
    s3 = build_furniture_layout_sheet_commands(5000, 15000, rooms)
    assert "KT-03" in " ".join(s3)

    # Sheet 4: KT-04 Door schedule
    s4 = build_door_schedule_sheet_commands(5000, 15000, [])
    assert "KT-04" in " ".join(s4)

    # Sheet 5: KT-05 Elevation
    s5 = build_finalized_sheets_commands("elevation", 5000, 15000, rooms)
    assert "KT-05" in " ".join(s5)
    assert "MẶT ĐỨNG CHÍNH CÔNG TRÌNH" in " ".join(s5)

    # Sheet 6: KT-06 Section
    s6 = build_finalized_sheets_commands("section", 5000, 15000, rooms)
    assert "KT-06" in " ".join(s6)
    assert "MẶT CẮT DỌC 1-1 QUA THANG" in " ".join(s6)

    # Sheet 7: KT-07 Ceiling & Lighting
    s7 = build_finalized_sheets_commands("ceiling_lighting", 5000, 15000, rooms)
    assert "KT-07" in " ".join(s7)

    # Sheet 8: KT-08 Roof & Drainage
    s8 = build_finalized_sheets_commands("roof_drainage", 5000, 15000, rooms)
    assert "KT-08" in " ".join(s8)

    # Sheet 9: KT-09 Stair details
    s9 = build_finalized_sheets_commands("stair_detail", 5000, 15000, rooms)
    assert "KT-09" in " ".join(s9)

    # Sheet 10: KT-10 WC details
    s10 = build_finalized_sheets_commands("wc_detail", 5000, 15000, rooms)
    assert "KT-10" in " ".join(s10)

    # Sheet 11: KT-11 Door details
    s11 = build_finalized_sheets_commands("door_detail", 5000, 15000, rooms)
    assert "KT-11" in " ".join(s11)

    # Full set of all 11 sheets
    s_full = build_finalized_sheets_commands(
        "full_project_set",
        5000,
        15000,
        floor_height_mm=3800.0,
        num_floors=2,
        num_risers=21,
        rooms=rooms,
    )
    s_full_str = " ".join(s_full)
    for code in ["KT-01", "KT-02", "KT-03", "KT-04", "KT-05", "KT-06", "KT-07", "KT-08", "KT-09", "KT-10", "KT-11"]:
        assert code in s_full_str


def test_dynamic_stairs_and_pagination():
    """Test dynamic stair calculation and dynamic door pagination."""
    from autocad_ai.core.finalizer import calculate_stair_parameters, build_door_details_paginated_commands

    # Dynamic stair check (h = H/N, b_raw = 250mm, b_finish = 270mm)
    stair_3600 = calculate_stair_parameters(floor_height_mm=3600.0, num_risers=21)
    assert stair_3600["riser_height_mm"] == 171.4
    assert stair_3600["tread_width_raw_mm"] == 250.0
    assert stair_3600["tread_width_finish_mm"] == 270.0

    stair_3900 = calculate_stair_parameters(floor_height_mm=3900.0, num_risers=23)
    assert stair_3900["riser_height_mm"] == 169.6
    assert stair_3900["tread_width_raw_mm"] == 250.0


    # Dynamic door pagination (10 doors -> 4 A3 sheets)
    doors_10 = [{"code": f"D{i}", "name": f"Door {i}", "width": 900, "height": 2200} for i in range(1, 11)]
    door_res = build_door_details_paginated_commands(doors_10, max_doors_per_sheet=3)
    assert door_res["total_doors"] == 10
    assert door_res["sheet_count"] == 4
    assert len(door_res["sheets"]) == 4
    assert door_res["sheets"][0]["code"] == "KT-11.01"
    assert door_res["sheets"][3]["code"] == "KT-11.04"




def test_detailed_estimator():
    """Test detailed construction BOQ calculation and CSV export."""
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        csv_path = tmp.name

    try:
        res = calculate_detailed_construction_boq(
            frontage_w_m=5.0,
            depth_l_m=15.0,
            num_floors=2,
            floor_height_m=3.6,
            num_bedrooms=3,
            num_bathrooms=2,
            output_csv_path=csv_path,
        )

        assert res["project_scope"]["total_floor_area_m2"] == 150.0
        assert res["summary"]["total_concrete_m3"] > 0
        assert res["summary"]["total_steel_ton"] > 0
        assert res["summary"]["brick_wall_220_m3"] > 0
        assert res["boq_items_count"] >= 10
        assert os.path.exists(csv_path)
        assert os.path.getsize(csv_path) > 100
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)


def test_inspector_compliance():
    """Test architectural compliance checking."""
    # Compliant living room
    res_pass = check_room_clear_dimensions(length_mm=5000, width_mm=4000, room_type="living")
    assert res_pass["is_standard_compliant"] is True
    assert res_pass["actual_area_m2"] == 20.0

    # Non-compliant small bedroom (< 9m2)
    res_fail = check_room_clear_dimensions(length_mm=2500, width_mm=2500, room_type="bedroom_single")
    assert res_fail["is_standard_compliant"] is False
    assert len(res_fail["warnings"]) > 0

    # Full plan audit
    from autocad_ai.core.inspector import audit_full_floor_plan
    sample_rooms = [
        {"name": "Phòng Khách", "y_start": 0, "y_end": 5000, "type": "living"},
        {"name": "Cầu Thang", "y_start": 5000, "y_end": 7500, "type": "stairs"},
        {"name": "Bếp & Ăn", "y_start": 7500, "y_end": 12000, "type": "kitchen"},
        {"name": "WC", "y_start": 12000, "y_end": 14000, "type": "wc"},
    ]
    audit_res = audit_full_floor_plan(width_mm=5000, length_mm=14000, rooms=sample_rooms, floor_height_mm=3600, num_risers=21)
    assert audit_res["is_compliant"] is True
    assert len(audit_res["passed_rules"]) >= 3



def test_plotter_commands():
    """Test standardized PDF plot command generation."""
    from autocad_ai.core.plotter import build_plot_single_sheet_commands, build_batch_plot_commands

    single = build_plot_single_sheet_commands(
        sheet_code="KT-01",
        window_p1=[-2000, -3000],
        window_p2=[12000, 17000],
        output_pdf_path="/tmp/test_kt01.pdf",
        paper_size="A3",
        plot_style="monochrome.ctb",
    )
    cmd_str = " ".join(single)
    assert "-PLOT" in cmd_str
    assert "DWG To PDF.pc3" in cmd_str
    assert "ISO full bleed A3" in cmd_str
    assert "monochrome.ctb" in cmd_str

    batch_full = build_batch_plot_commands(output_directory="/tmp/cad_test_batch", batch_scope="full_project_set")
    assert batch_full["sheet_count"] == 11
    assert len(batch_full["pdf_files"]) == 11

    batch_floors = build_batch_plot_commands(output_directory="/tmp/cad_test_batch", batch_scope="all_floor_plans")
    assert batch_floors["sheet_count"] == 4
    assert len(batch_floors["pdf_files"]) == 4



def test_knowledge_engine():
    """Test in-code architectural reference library extraction engine."""
    from autocad_ai.knowledge.engine import (
        get_library_topics,
        get_full_topic_document,
        search_reference_library,
        get_room_guidelines,
    )

    # 1. List topics
    topics = get_library_topics()
    assert len(topics) >= 7
    categories = [t["category"] for t in topics]
    assert "01-tieu-chuan-khong-gian" in categories
    assert "03-he-thong-mep-dien-nuoc" in categories

    # 2. Get room guidelines
    kitchen_guide = get_room_guidelines("kitchen")
    assert "guideline_markdown" in kitchen_guide
    assert "Tam giác" in kitchen_guide["guideline_markdown"] or "Bếp" in kitchen_guide["guideline_markdown"]

    stair_guide = get_room_guidelines("stairs")
    assert "cau-thang-va-hanh-lang.md" == stair_guide["target_document"]

    # 3. Search reference library
    search_res = search_reference_library("100mm")
    assert len(search_res) > 0

    # 4. Get specific topic document
    doc = get_full_topic_document("cau-thang-va-hanh-lang")
    assert doc is not None
    assert "Blondel" in doc["content"]


def test_servers_registration():
    """Test that all 8 core Vietnamese business commands are registered on Mac and Win servers."""
    expected_vietnamese_tools = {
        "cad_ve_moi",
        "cad_chinh_sua",
        "cad_hoan_thien_ho_so",
        "cad_du_toan",
        "cad_kiem_tra",
        "cad_gui_lenh",
        "cad_in_pdf",
        "cad_tra_cuu_quy_chuan",
    }

    from autocad_ai.servers.mac_server import mcp as mac_mcp
    from autocad_ai.servers.win_server import mcp as win_mcp

    import asyncio
    mac_tools = {t.name for t in asyncio.run(mac_mcp.list_tools())}
    win_tools = {t.name for t in asyncio.run(win_mcp.list_tools())}

    assert expected_vietnamese_tools.issubset(mac_tools)
    assert expected_vietnamese_tools.issubset(win_tools)


def test_integration_cad_ve_moi():
    """Integration test: call cad_ve_moi through MCP tool layer to catch TypeError."""
    from autocad_ai.servers.mac_server import cad_ve_moi
    rooms = [
        {"name": "Phòng Khách", "y_start": 2500, "y_end": 7000, "type": "living"},
        {"name": "Cầu Thang", "y_start": 7000, "y_end": 9500, "type": "stairs"},
    ]
    # This call goes through the exact same path as MCP tool invocation
    result = cad_ve_moi(
        frontage_width_mm=5000.0,
        depth_length_mm=15000.0,
        rooms=rooms,
    )
    assert result is not None
    assert "status" in result or "command_count" in result or "script_file" in result


def test_integration_cad_chinh_sua():
    """Integration test: call cad_chinh_sua through MCP tool layer to catch TypeError."""
    from autocad_ai.servers.mac_server import cad_chinh_sua
    result = cad_chinh_sua(
        action="stretch_room",
        target="wall",
        dx=500.0,
        dy=0.0,
        window_p1=[1000, 2000],
        window_p2=[4000, 5000],
    )
    assert result is not None
    assert "status" in result or "command_count" in result or "script_file" in result
