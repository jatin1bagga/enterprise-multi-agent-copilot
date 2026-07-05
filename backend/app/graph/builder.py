import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.data_analysis.node import data_analysis_node
from app.agents.forecast.node import forecast_node
from app.agents.mail.node import mail_node
from app.agents.python_exec.node import python_exec_node
from app.agents.rag.node import rag_node
from app.agents.report.node import report_node
from app.core.config import Settings
from app.graph.nodes.load_memory_node import load_memory_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.save_memory_node import save_memory_node
from app.graph.nodes.synthesize_node import synthesize_node
from app.graph.router import route_after_agent, route_from_planner
from app.graph.state import GraphState

GRAPH_NAME = "operations_copilot_graph"

_AGENT_NODES = {
    "rag": rag_node,
    "data_analysis": data_analysis_node,
    "python_exec": python_exec_node,
    "report": report_node,
    "forecast": forecast_node,
    "mail": mail_node,
}


async def build_graph(settings: Settings) -> CompiledStateGraph:
    graph = StateGraph(GraphState)

    graph.add_node("load_memory", load_memory_node)
    graph.add_node("planner", planner_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("save_memory", save_memory_node)
    for agent_name, node_fn in _AGENT_NODES.items():
        graph.add_node(agent_name, node_fn)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "planner")

    graph.add_conditional_edges(
        "planner",
        route_from_planner,
        {**{name: name for name in _AGENT_NODES}, "synthesize": "synthesize"},
    )

    for agent_name in _AGENT_NODES:
        graph.add_conditional_edges(
            agent_name,
            route_after_agent,
            {**{name: name for name in _AGENT_NODES}, "planner": "planner"},
        )

    graph.add_edge("synthesize", "save_memory")
    graph.add_edge("save_memory", END)

    conn = await aiosqlite.connect(str(settings.sqlite_abs_path))
    checkpointer = AsyncSqliteSaver(conn)

    return graph.compile(checkpointer=checkpointer, name=GRAPH_NAME)
