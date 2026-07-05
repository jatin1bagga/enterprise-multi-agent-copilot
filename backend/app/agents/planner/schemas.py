from pydantic import BaseModel, Field

from app.graph.state import AgentName


class PlanStep(BaseModel):
    step_id: str = Field(description="Short unique id, e.g. 's1', 's2'.")
    agent: AgentName = Field(description="Which agent should execute this step.")
    instruction: str = Field(description="Specific, self-contained instruction for that agent.")
    depends_on: list[str] = Field(
        default_factory=list, description="step_ids that must complete before this step can run."
    )


class ExecutionPlan(BaseModel):
    steps: list[PlanStep] = Field(
        default_factory=list,
        description="Ordered/parallelizable steps needed to answer the user. Empty if no agent is needed.",
    )
