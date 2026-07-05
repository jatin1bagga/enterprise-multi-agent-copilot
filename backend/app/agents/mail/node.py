import re
from typing import Any

from app.agents.base import agent_node, current_step
from app.agents.mail.service import send_email
from app.core.config import get_settings
from app.graph.state import GraphState

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

_TYPE_KEYWORDS = {
    "report_pdf": ("pdf",),
    "report_pptx": ("pptx", "powerpoint", "ppt", "deck", "slides"),
    "report_md": ("markdown", "md"),
    "plot": ("chart", "graph", "plot", "image", "png"),
    "table": ("table", "csv"),
}


def _extract_recipient(step_instruction: str, user_query: str) -> str | None:
    match = EMAIL_RE.search(step_instruction) or EMAIL_RE.search(user_query)
    # the greedy domain group can swallow a sentence-ending period, e.g. "...to alice@x.com."
    return match.group(0).rstrip(".") if match else None


def _select_attachments(instruction: str, state: GraphState) -> list[dict]:
    instruction_lower = instruction.lower()
    produced_this_turn = state.get("artifacts") or []
    prior_artifacts = (state.get("context") or {}).get("prior_artifacts") or []

    candidates = produced_this_turn or prior_artifacts
    if not candidates:
        return []

    requested_types = {
        artifact_type
        for artifact_type, keywords in _TYPE_KEYWORDS.items()
        if any(kw in instruction_lower for kw in keywords)
    }
    if not requested_types:
        return [c for c in candidates if str(c.get("artifact_type", "")).startswith("report")] or candidates

    return [c for c in candidates if c.get("artifact_type") in requested_types]


@agent_node("mail")
def mail_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    instruction = step["instruction"]

    recipient = _extract_recipient(instruction, state["user_query"])
    if not recipient:
        return {
            "agent_outputs": {
                step["step_id"]: (
                    "I couldn't find a recipient email address in your request, so no email was sent. "
                    "Please include an email address, e.g. 'email the report to alice@example.com'."
                )
            }
        }

    attachments = _select_attachments(instruction, state)
    attachment_paths = [a["file_path"] for a in attachments if a.get("file_path")]

    settings = get_settings()
    subject = "Your requested report - Enterprise Operations Copilot"
    body = (
        f"Hi,\n\nAs requested, please find attached the output for:\n\"{state['user_query']}\"\n\n"
        f"— Enterprise Operations Copilot"
    )

    send_email(settings, recipient, subject, body, attachment_paths)

    attachment_note = (
        f" with {len(attachment_paths)} attachment(s): {', '.join(a['title'] for a in attachments)}"
        if attachment_paths
        else " (no matching attachments were found, so it was sent without one)"
    )
    return {
        "agent_outputs": {
            step["step_id"]: f"Emailed the results to {recipient}{attachment_note}."
        }
    }
