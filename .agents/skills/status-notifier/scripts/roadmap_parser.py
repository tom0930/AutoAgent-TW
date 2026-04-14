import re
import sys
from pathlib import Path

# Add project root scripts dir for aa_constants
script_dir = Path(__file__).parent.resolve()
sys.path.append(str(script_dir.parent.parent.parent.parent / "scripts"))

try:
    import aa_constants
except ImportError:
    # Minimal fallback or let it fail if not in AA env
    aa_constants = None

def get_roadmap_mermaid():
    if aa_constants:
        roadmap_path = aa_constants.get_planning_dir() / "ROADMAP.md"
        status_path = aa_constants.get_state_dir() / "STATE.md"
    else:
        roadmap_path = Path(".planning/ROADMAP.md")
        status_path = Path(".planning/STATE.md")
    
    if not roadmap_path.exists():
        return "graph TD\n  Error[ROADMAP.md not found]"
    
    with open(roadmap_path, "r", encoding="utf-8") as f:
        roadmap_content = f.read()
    
    statuses = {}
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            status_content = f.read()
            # Extract PhaeStatuses: "- Phase X: ... [STATUS]"
            matches = re.finditer(r"- Phase (\d+): (.*?) \[(.*?)\]", status_content)
            for m in matches:
                statuses[int(m.group(1))] = m.group(3)

    # Extract Phases from ROADMAP.md: "- [ ] Phase X: Title"
    matches = re.finditer(r"- \[(.)\] Phase (\d+): (.*)", roadmap_content)
    
    mermaid_lines = ["graph TD"]
    phases = []
    
    for match in matches:
        is_done = match.group(1).upper() == "X"
        p_num = int(match.group(2))
        p_title = match.group(3).strip()
        
        # Escape quotes for Mermaid
        p_title_esc = p_title.replace('"', "'")
        
        # Map status to Mermaid classes
        p_class = "done" if is_done else "pending"
        
        # If this is the current phase N, mark it as running
        # (Heuristic: first unchecked phase is running)
        if not is_done and "running" not in [l.split(":::")[-1] for l in mermaid_lines if ":::" in l]:
            p_class = "running"
        
        node_id = f"P{p_num}"
        phases.append(node_id)
        mermaid_lines.append(f'  {node_id}["Phase {p_num}: {p_title_esc}"]:::{p_class}')

    # Connect nodes
    for i in range(len(phases) - 1):
        mermaid_lines.append(f'  {phases[i]} --> {phases[i+1]}')


    # Add Class Definitions
    mermaid_lines.append('  classDef done fill:#238636,color:white,stroke:none')
    mermaid_lines.append('  classDef running fill:#4ade80,color:black,stroke-width:3px,stroke:#fff')
    mermaid_lines.append('  classDef pending fill:#21262d,color:#8b949e,stroke:#30363d')
    mermaid_lines.append('  classDef fail fill:#f85149,color:white,stroke:none')
    
    return "\n".join(mermaid_lines)

if __name__ == "__main__":
    print(get_roadmap_mermaid())
