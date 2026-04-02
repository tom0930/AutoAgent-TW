import re
from pathlib import Path

def get_roadmap_mermaid():
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

    # Extract Phases from ROADMAP.md: "## Phase X: Title"
    phase_blocks = re.split(r"## Phase ", roadmap_content)[1:]
    
    mermaid_lines = ["graph TD"]
    phases = []
    
    for i, block in enumerate(phase_blocks):
        lines = block.split("\n")
        header = lines[0].strip()
        # header format: "1: Title"
        match = re.match(r"(\d+): (.*)", header)
        if match:
            p_num = int(match.group(1))
            p_title = match.group(2).strip()
            
            # Escape quotes for Mermaid
            p_title_esc = p_title.replace('"', "'")
            
            # Map status to Mermaid classes
            p_status = statuses.get(p_num, "PENDING")
            p_class = "pending"
            if p_status == "DONE":
                p_class = "done"
            elif p_status == "PLANNED": # For visualization, planned means ready or current
                 p_class = "running"
            elif "RUNNING" in p_status:
                p_class = "running"
            elif "FAIL" in p_status:
                p_class = "fail"
            
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
