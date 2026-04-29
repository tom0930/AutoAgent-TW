from pydantic import BaseModel, Field
from typing import List

class AgentPlan(BaseModel):
    role: str = Field(..., description="The role of the agent generating this plan (e.g., Architect, Security, UX)")
    confidence: float = Field(..., description="Confidence level of the proposed plan from 0.0 to 1.0")
    plan_section: str = Field(..., description="The markdown formatted plan section proposed by this agent")
    dependencies: List[str] = Field(default_factory=list, description="List of internal or external dependencies identified")
    risks: List[str] = Field(default_factory=list, description="List of risks identified by this agent")
    conflicts_with: List[str] = Field(default_factory=list, description="Potential conflicts with other areas/technologies")

class ConflictReport(BaseModel):
    has_conflict: bool = Field(..., description="Whether a conflict exists between the agents' plans")
    conflict_dimensions: List[str] = Field(default_factory=list, description="Dimensions where plans conflict (e.g., Architecture vs Security)")
    description: str = Field(..., description="Detailed description of the conflict")

class DecisionMatrixOption(BaseModel):
    option_id: int
    title: str
    pros: List[str]
    cons: List[str]
    risk_level: str

class DecisionMatrix(BaseModel):
    conflict_summary: str
    options: List[DecisionMatrixOption]
