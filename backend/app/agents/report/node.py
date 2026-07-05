from typing import Any

from app.agents.base import agent_node, current_step
from app.agents.report.markdown_report import build_markdown_report
from app.agents.report.pdf_export import markdown_to_pdf
from app.agents.report.pptx_export import build_pptx_report
from app.graph.state import GraphState
from app.utils.files import artifact_path
from app.utils.ids import new_id


def _sections_from_outputs(state: GraphState) -> list[tuple[str, str]]:
    plan = state.get("plan") or []
    agent_outputs = state.get("agent_outputs") or {}
    sections = []
    for step in plan:
        if step["agent"] == "report":
            continue
        content = agent_outputs.get(step["step_id"])
        if content:
            sections.append((f"{step['agent'].replace('_', ' ').title()} findings", content))
    return sections or [("Summary", "No prior agent output was available to include in this report.")]


@agent_node("report")
def report_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    sections = _sections_from_outputs(state)
    title = "Operations Copilot Report"

    markdown_text = build_markdown_report(title, state["user_query"], sections)

    base_name = new_id("report_")
    md_path = artifact_path(f"{base_name}.md")
    pdf_path = artifact_path(f"{base_name}.pdf")
    pptx_path = artifact_path(f"{base_name}.pptx")

    md_path.write_text(markdown_text, encoding="utf-8")
    markdown_to_pdf(markdown_text, pdf_path)
    build_pptx_report(title, sections, pptx_path)

    artifacts = [
        {
            "artifact_type": "report_md",
            "file_path": str(md_path),
            "mime_type": "text/markdown",
            "title": f"{title} (Markdown)",
        },
        {
            "artifact_type": "report_pdf",
            "file_path": str(pdf_path),
            "mime_type": "application/pdf",
            "title": f"{title} (PDF)",
        },
        {
            "artifact_type": "report_pptx",
            "file_path": str(pptx_path),
            "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "title": f"{title} (PowerPoint)",
        },
    ]

    return {
        "agent_outputs": {step["step_id"]: f"Report generated with {len(sections)} section(s): Markdown, PDF, and PowerPoint versions are available for download."},
        "artifacts": artifacts,
    }
