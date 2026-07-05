import logging
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.agents.base import agent_node, current_step
from app.agents.data_analysis.eda import load_tabular_file, run_eda
from app.agents.data_analysis.insights import generate_insights
from app.utils.files import artifact_path, find_latest_tabular_file
from app.utils.ids import new_id
from app.graph.state import GraphState

logger = logging.getLogger(__name__)


def _plot_correlation_heatmap(eda_result: dict) -> str | None:
    correlations = eda_result.get("correlations")
    if not correlations:
        return None

    import pandas as pd

    corr_df = pd.DataFrame(correlations)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr_df.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_df.columns)))
    ax.set_xticklabels(corr_df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr_df.index)))
    ax.set_yticklabels(corr_df.index)
    fig.colorbar(im, ax=ax)
    ax.set_title("Correlation heatmap")
    fig.tight_layout()

    filename = f"{new_id('corr_')}.png"
    path = artifact_path(filename)
    fig.savefig(path)
    plt.close(fig)
    return str(path)


@agent_node("data_analysis")
def data_analysis_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    context = state.get("context", {})

    file_meta = find_latest_tabular_file(context)
    if file_meta is None:
        return {"agent_outputs": {step["step_id"]: "No CSV/Excel file has been uploaded to analyze."}}

    df = load_tabular_file(file_meta["stored_path"])
    eda_result = run_eda(df)
    insights = generate_insights(eda_result, step["instruction"])

    artifacts = []
    try:
        plot_path = _plot_correlation_heatmap(eda_result)
    except Exception:
        logger.exception("Correlation heatmap generation failed; continuing without it")
        plot_path = None
    if plot_path:
        artifacts.append(
            {
                "artifact_type": "plot",
                "file_path": plot_path,
                "mime_type": "image/png",
                "title": f"Correlation heatmap - {file_meta['filename']}",
            }
        )
    elif eda_result.get("correlations"):
        logger.warning("Correlations were present but no heatmap artifact was produced")

    output_text = f"Analysis of {file_meta['filename']}:\n\n{insights}"

    return {
        "agent_outputs": {step["step_id"]: output_text},
        "artifacts": artifacts,
    }
