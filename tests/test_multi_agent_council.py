"""Test Multi-Agent Council System for AutoCAD AI."""

import pytest
from autocad_ai.agents.concept_agent import ConceptArchitectAgent
from autocad_ai.agents.inspector_agent import InspectorCriticAgent
from autocad_ai.agents.structure_agent import StructureMEPAgent
from autocad_ai.agents.council_orchestrator import ArchitecturalCouncilOrchestrator


def test_concept_agent_proposal():
    """Test KTS_Concept generating initial layout proposal."""
    agent = ConceptArchitectAgent()
    brief = {
        "width_m": 12.0,
        "length_m": 12.0,
        "num_floors": 3,
        "land_size_m": [30.0, 30.0],
        "main_orientation": "Tây Nam",
    }
    proposal = agent.propose_initial_layout(brief)
    
    assert proposal["author"] == "KTS_Concept"
    assert proposal["building_width_mm"] == 12000.0
    assert "floor_1" in proposal["floors"]
    assert "floor_2" in proposal["floors"]
    assert "floor_3" in proposal["floors"]
    assert len(proposal["floors"]["floor_1"]["rooms"]) >= 6


def test_inspector_agent_critique():
    """Test KTS_Inspector_QC reviewing and grading proposal."""
    inspector = InspectorCriticAgent()
    concept = ConceptArchitectAgent()
    brief = {"width_m": 12.0, "length_m": 12.0, "num_floors": 3}
    proposal = concept.propose_initial_layout(brief)

    review = inspector.review_proposal(proposal)
    assert "score" in review
    assert review["score"] >= 8.0
    assert "is_approved" in review
    assert isinstance(review["critiques"], list)


def test_structure_agent_review():
    """Test KySu_KetCau reviewing columns and MEP."""
    struct = StructureMEPAgent()
    concept = ConceptArchitectAgent()
    brief = {"width_m": 12.0, "length_m": 12.0, "num_floors": 3}
    proposal = concept.propose_initial_layout(brief)

    review = struct.review_structural_feasibility(proposal)
    assert review["is_approved"] is True
    assert len(review["recommended_grid_x"]) == 4
    assert 9000.0 not in review["recommended_grid_x"]  # Axis at 9000 must be removed


def test_council_orchestrator_debate_and_consensus():
    """Test full multi-agent debate loop converging to consensus."""
    council = ArchitecturalCouncilOrchestrator()
    brief = {
        "width_m": 12.0,
        "length_m": 12.0,
        "num_floors": 3,
        "land_size_m": [30.0, 30.0],
        "main_orientation": "Tây Nam",
    }
    result = council.convene_council_session(brief, max_rounds=3)

    assert result["council_status"] == "CONSENSUS_REACHED"
    assert result["council_resolution"]["final_score"] >= 9.5
    assert len(result["session_log"]) >= 2
    assert "floor_1" in result["final_approved_proposal"]["floors"]
