import logging
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from app.agents.base import agent_node, current_step
from app.agents.data_analysis.eda import load_tabular_file
from app.agents.forecast.narrative import generate_forecast_narrative
from app.agents.forecast.service import compute_forecast
from app.core.config import get_settings
from app.graph.state import GraphState
from app.utils.files import artifact_path, find_latest_tabular_file
from app.utils.ids import new_id

logger = logging.getLogger(__name__)


def _plot_forecast(result: dict, filename_title: str) -> str:
    historical = result["historical"]
    forecast = result["forecast"]

    hist_labels = [p["period"] for p in historical]
    hist_values = [p["value"] for p in historical]
    fcst_labels = [p["period"] for p in forecast]
    fcst_values = [p["value"] for p in forecast]
    fcst_lower = [p["lower"] for p in forecast]
    fcst_upper = [p["upper"] for p in forecast]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    hist_x = list(range(len(hist_values)))
    fcst_x = list(range(len(hist_values) - 1, len(hist_values) + len(fcst_values)))
    fcst_values_with_join = [hist_values[-1], *fcst_values]
    fcst_lower_with_join = [hist_values[-1], *fcst_lower]
    fcst_upper_with_join = [hist_values[-1], *fcst_upper]

    ax.plot(hist_x, hist_values, marker="o", label="Historical", color="#2563eb")
    ax.plot(fcst_x, fcst_values_with_join, marker="o", linestyle="--", label="Forecast", color="#f97316")
    ax.fill_between(fcst_x, fcst_lower_with_join, fcst_upper_with_join, color="#f97316", alpha=0.15)

    ax.set_xticks(hist_x + fcst_x[1:])
    ax.set_xticklabels(hist_labels + fcst_labels, rotation=45, ha="right")
    ax.set_ylabel(result["metric_column"])
    ax.set_title(f"{result['metric_column']} forecast ({filename_title})")
    ax.legend()
    fig.tight_layout()

    filename = f"{new_id('forecast_')}.png"
    path = artifact_path(filename)
    fig.savefig(path)
    plt.close(fig)
    return str(path)


@agent_node("forecast")
def forecast_node(state: GraphState) -> dict[str, Any]:
    step = current_step(state)
    context = state.get("context", {})

    file_meta = find_latest_tabular_file(context)
    if file_meta is None:
        return {
            "agent_outputs": {step["step_id"]: "No CSV/Excel file has been uploaded to forecast."}
        }

    df = load_tabular_file(file_meta["stored_path"])
    settings = get_settings()
    result = compute_forecast(df, step["instruction"], settings.forecast_periods_ahead)
    narrative = generate_forecast_narrative(result, step["instruction"])

    artifacts = []
    try:
        plot_path = _plot_forecast(result, file_meta["filename"])
        artifacts.append(
            {
                "artifact_type": "plot",
                "file_path": plot_path,
                "mime_type": "image/png",
                "title": f"Forecast - {result['metric_column']}",
            }
        )
    except Exception:
        logger.exception("Forecast chart generation failed; continuing with narrative only")

    output_text = f"Forecast for {result['metric_column']} ({file_meta['filename']}):\n\n{narrative}"

    return {
        "agent_outputs": {step["step_id"]: output_text},
        "artifacts": artifacts,
    }
