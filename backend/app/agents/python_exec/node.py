from typing import Any

from app.agents.base import agent_node, current_step
from app.agents.data_analysis.eda import load_tabular_file
from app.agents.python_exec.codegen import generate_code
from app.agents.python_exec.sandbox import run_in_sandbox
from app.graph.state import GraphState
from app.utils.files import find_latest_tabular_file

_MIME_TYPES = {".png": "image/png", ".csv": "text/csv"}


def _find_data_path(context: dict) -> str | None:
    file_meta = find_latest_tabular_file(context)
    return file_meta["stored_path"] if file_meta else None


def _describe_columns(data_path: str | None) -> str | None:
    if not data_path:
        return None
    try:
        df = load_tabular_file(data_path)
    except Exception:
        return None
    return ", ".join(f"{col} ({dtype})" for col, dtype in df.dtypes.astype(str).items())


def _previous_error_for_step(state: GraphState, step_id: str) -> str | None:
    for err in reversed(state.get("errors") or []):
        if err.get("step_id") == step_id:
            return err["error"]
    return None


@agent_node("python_exec")
def python_exec_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    context = state.get("context", {})
    data_path = _find_data_path(context)

    previous_error = _previous_error_for_step(state, step["step_id"])
    columns_desc = _describe_columns(data_path)
    code = generate_code(step["instruction"], data_path, columns_desc, previous_error)

    result = run_in_sandbox(code, data_path)

    if result.timed_out:
        raise RuntimeError(f"Sandbox execution timed out.\nSTDERR:\n{result.stderr}")
    if result.killed_for_memory:
        raise RuntimeError(f"Sandbox execution exceeded memory limit.\nSTDERR:\n{result.stderr}")
    if result.returncode != 0:
        raise RuntimeError(f"Generated code failed:\n{result.stderr}\n\nCode was:\n{code}")

    artifacts = []
    for path in result.output_files:
        mime = _MIME_TYPES.get(path.suffix.lower(), "application/octet-stream")
        artifacts.append(
            {
                "artifact_type": "plot" if mime.startswith("image") else "table",
                "file_path": str(path),
                "mime_type": mime,
                "title": path.name,
            }
        )

    output_text = result.stdout.strip() or "Code executed successfully with no printed output."

    return {
        "agent_outputs": {step["step_id"]: output_text},
        "artifacts": artifacts,
    }
