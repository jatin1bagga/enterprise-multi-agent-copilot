import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.factory import get_chat_model

INSIGHTS_SYSTEM_PROMPT = """You are a business data analyst. Given computed EDA statistics for a
dataset (shape, missing values, numeric summary, correlations), write a concise business-focused
summary: 3-6 bullet points covering data quality issues (missing values), notable relationships
(correlations), and any actionable observations. Be specific and reference actual column names and
numbers from the stats. Do not repeat the raw JSON."""


def generate_insights(eda_result: dict, user_instruction: str) -> str:
    llm = get_chat_model(temperature=0.2)
    response = llm.invoke(
        [
            SystemMessage(content=INSIGHTS_SYSTEM_PROMPT),
            HumanMessage(
                content=f"User request: {user_instruction}\n\nEDA statistics (JSON):\n{json.dumps(eda_result)}"
            ),
        ]
    )
    return response.content
