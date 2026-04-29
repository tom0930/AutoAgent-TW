import pytest
from scripts.execution.dag import build_dag

def test_build_dag_no_dependencies():
    consensus_result = {
        "tasks": [
            {"id": "t1", "role": "dev", "target_files": ["a.py"]},
            {"id": "t2", "role": "ui", "target_files": ["b.js"]}
        ]
    }
    
    nodes = build_dag(consensus_result)
    
    assert len(nodes) == 2
    # Without dependencies, topological sort returns nodes in order of definition (lexicographical usually, but implementation dependent).
    # We mainly check length and node objects.
    assert {n.id for n in nodes} == {"t1", "t2"}

def test_build_dag_with_dependencies():
    consensus_result = {
        "tasks": [
            {"id": "t1", "role": "dev", "target_files": ["b.py"], "dependencies": ["t2"]},
            {"id": "t2", "role": "dev", "target_files": ["a.py"]}
        ]
    }
    
    nodes = build_dag(consensus_result)
    
    assert len(nodes) == 2
    assert nodes[0].id == "t2"
    assert nodes[1].id == "t1"

def test_build_dag_with_cycle_fallback():
    # t1 depends on t2, t2 depends on t1
    consensus_result = {
        "tasks": [
            {"id": "t1", "role": "dev", "dependencies": ["t2"]},
            {"id": "t2", "role": "dev", "dependencies": ["t1"]}
        ]
    }
    
    # Cycle should be caught, fallback to input order [t1, t2]
    nodes = build_dag(consensus_result)
    
    assert len(nodes) == 2
    assert nodes[0].id == "t1"
    assert nodes[1].id == "t2"
