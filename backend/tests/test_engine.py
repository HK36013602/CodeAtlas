from app.analysis.engine import EDGE_PAIRS, build_snapshot, find_cycles

def test_cycles_are_detected():
    cycles = find_cycles(EDGE_PAIRS)
    assert any(set(cycle) >= {"payment", "risk"} for cycle in cycles)

def test_snapshot_is_deterministic():
    assert build_snapshot(7)["nodes"] == build_snapshot(7)["nodes"]

def test_snapshot_contract():
    result = build_snapshot()
    assert result["summary"]["modules"] == len(result["nodes"])
    assert result["summary"]["cycles"] >= 3
    assert result["repository"]["synthetic"] is True
