import operator
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

AgentName = Literal["rag", "data_analysis", "python_exec", "report", "forecast", "mail"]


class PlannedStep(TypedDict):
    step_id: str
    agent: AgentName
    instruction: str
    depends_on: list[str]
    status: Literal["pending", "running", "done", "failed"]


def merge_dicts(left: dict, right: dict) -> dict:
    return {**left, **right}


class GraphState(TypedDict):
    conversation_id: str
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    context: dict

    plan: list[PlannedStep]
    current_step_index: int

    agent_outputs: Annotated[dict, merge_dicts]
    citations: Annotated[list[dict], operator.add]
    artifacts: Annotated[list[dict], operator.add]
    errors: Annotated[list[dict], operator.add]
    agent_trace: Annotated[list[dict], operator.add]
    retry_counts: dict[str, int]

    final_answer: str
