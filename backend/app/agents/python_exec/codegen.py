import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.factory import get_chat_model

CODEGEN_SYSTEM_PROMPT = """You write self-contained Python scripts for a data analysis sandbox.
Rules:
- Only use these libraries: pandas, numpy, matplotlib, plotly, math, statistics, json, io, itertools.
- matplotlib is already configured with the "Agg" backend; do not call plt.show().
- A variable `DATA_PATH` is predefined as a string with the path to the user's uploaded data file
  (CSV or Excel), or None if no file was uploaded. Load it yourself with pandas if you need it.
- If you produce a chart, save it to a file named exactly "output.png" (e.g. plt.savefig("output.png")).
- If you produce a table result, save it to a file named exactly "output_table.csv"
  (e.g. df.to_csv("output_table.csv", index=False)).
- Print a short human-readable summary of what you computed using print().
- Output ONLY a single Python code block, no explanations before or after."""


def _extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def generate_code(
    instruction: str,
    data_path: str | None,
    columns_desc: str | None = None,
    previous_error: str | None = None,
) -> str:
    llm = get_chat_model(temperature=0.1)

    user_content = f"Task: {instruction}\nDATA_PATH will be: {data_path!r}"
    if columns_desc:
        user_content += f"\nThe file at DATA_PATH has exactly these columns (name (dtype)): {columns_desc}"
        user_content += "\nUse these exact column names (case-sensitive) - do not guess or rename them."
    if previous_error:
        user_content += (
            f"\n\nYour previous attempt failed with this error, fix it:\n{previous_error}"
        )

    response = llm.invoke(
        [
            SystemMessage(content=CODEGEN_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
    )
    return _extract_code(response.content)
