from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.base import agent_node, current_step
from app.agents.rag.retrieve import retrieve_chunks
from app.graph.state import GraphState
from app.llm.factory import get_chat_model

RAG_SYSTEM_PROMPT = """You answer questions using only the provided document excerpts. Cite the
source file and page for every claim, in the form (filename, p.N). If the excerpts don't contain
the answer, say so plainly instead of guessing."""


@agent_node("rag")
def rag_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    query = step["instruction"]

    citations = retrieve_chunks(state["conversation_id"], query, k=5)

    if not citations:
        answer = "No relevant content was found in the uploaded documents for this request."
    else:
        excerpts = "\n\n".join(
            f"[{c.source_file}, p.{c.page}]: {c.snippet}" for c in citations
        )
        llm = get_chat_model(temperature=0.0)
        response = llm.invoke(
            [
                SystemMessage(content=RAG_SYSTEM_PROMPT),
                HumanMessage(content=f"Question: {query}\n\nExcerpts:\n{excerpts}"),
            ]
        )
        answer = response.content

    return {
        "agent_outputs": {step["step_id"]: answer},
        "citations": [c.model_dump() for c in citations],
    }
