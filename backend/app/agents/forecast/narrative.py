import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.factory import get_chat_model

NARRATIVE_SYSTEM_PROMPT = """You are a business analyst writing a short forecast summary for an
operations audience. Given a computed linear-trend forecast (historical points, forecasted future
points, and trend direction), write 3-5 concise sentences: state the trend, the forecasted values
with their period labels, and one caveat about this being a simple linear projection from limited
historical data (not a substitute for a full time-series model). Reference actual numbers from the
data. Do not invent figures beyond what is given."""


def generate_forecast_narrative(forecast_result: dict, user_instruction: str) -> str:
    llm = get_chat_model(temperature=0.2)
    response = llm.invoke(
        [
            SystemMessage(content=NARRATIVE_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"User request: {user_instruction}\n\n"
                    f"Forecast data (JSON):\n{json.dumps(forecast_result)}"
                )
            ),
        ]
    )
    return response.content
