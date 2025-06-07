import pytest
from agents.orchestrator import EnhancedTravelOrchestrator

def test_orchestrator_run():
    orchestrator = EnhancedTravelOrchestrator()
    result = orchestrator.run("Tôi muốn đi Hà Nội 2 ngày.")
    assert "HÀ NỘI" in result
    assert "ĐỊA ĐIỂM" in result
    assert "ẨM THỰC" in result
    assert "LỊCH TRÌNH" in result