from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.state import GraphState
from app.llm.factory import get_chat_model

SYNTHESIZE_SYSTEM_PROMPT = """You are the final-answer composer for an enterprise operations copilot.
You are given prior conversation history, the outputs already produced by specialist agents for
this turn (if any), and the current user request. Write a clear, well-structured answer in Markdown
that directly addresses the request, using the agent outputs as your source of truth for anything
agent-related. Do not invent citations, numbers, or file names beyond what is given to you. If a
step failed, briefly acknowledge the limitation and answer with whatever is still available. If no
agents ran, answer directly using the conversation history and your own knowledge."""


def synthesize_node(state: GraphState) -> dict[str, Any]:
    agent_outputs = state.get("agent_outputs") or {}
    errors = state.get("errors") or []
    plan = state.get("plan") or []

    if not plan and not agent_outputs:
        context_block = "(No specialist agents were needed for this request.)"
    else:
        lines = []
        for step in plan:
            output = agent_outputs.get(step["step_id"])
            if output is not None:
                lines.append(f"### Result from {step['agent']} (step {step['step_id']})\n{output}")
            else:
                lines.append(f"### Step {step['step_id']} ({step['agent']}) failed to produce a result.")
        for err in errors:
            lines.append(f"(Note: agent '{err['agent']}' encountered an error: {err['error']})")
        context_block = "\n\n".join(lines)

    recent_messages = (state.get("context") or {}).get("recent_messages") or []
    history_block = (
        "\n".join(f"{m['role']}: {m['content']}" for m in recent_messages[-10:])
        or "(no prior messages in this conversation)"
    )

    llm = get_chat_model(temperature=0.2)
    messages = [
        SystemMessage(content=SYNTHESIZE_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Conversation history:\n{history_block}\n\n"
                f"Current user request: {state['user_query']}\n\nAgent outputs:\n{context_block}"
            )
        ),
    ]

    chunks = []
    for chunk in llm.stream(messages):
        if chunk.content:
            chunks.append(chunk.content)
    final_answer = "".join(chunks).strip() or "I wasn't able to produce an answer for this request."

    return {"final_answer": final_answer}
