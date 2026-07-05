import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from smoke_test import BASE_URL, SAMPLE_DIR, sse_events  # noqa: E402

import httpx  # noqa: E402


def ask(client: httpx.Client, conversation_id: str, message: str) -> dict:
    events_seen = []
    final_payload = None
    with client.stream(
        "POST", f"/api/conversations/{conversation_id}/chat", json={"message": message}
    ) as response:
        for event_name, data in sse_events(response):
            events_seen.append((event_name, data))
            if event_name == "error":
                raise RuntimeError(data)
            if event_name == "final":
                final_payload = data
    for name, data in events_seen:
        if name in ("plan", "agent_status"):
            print(f"  [{name}]", data)
    return final_payload


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=180)

    conversation = client.post("/api/conversations", json={"title": "Mail+Forecast test"}).json()
    conversation_id = conversation["id"]
    print("conversation:", conversation_id)

    with open(SAMPLE_DIR / "sample.csv", "rb") as f:
        resp = client.post(
            f"/api/conversations/{conversation_id}/files",
            files={"file": ("sample.csv", f, "text/csv")},
        )
    resp.raise_for_status()
    print("uploaded:", resp.json())

    print("\n--- Turn 1: forecast ---")
    forecast_answer = ask(
        client,
        conversation_id,
        "Forecast the revenue for the next few periods based on this data.",
    )
    print("answer:\n", forecast_answer["content"])
    print("artifacts:", forecast_answer.get("artifacts"))
    assert forecast_answer.get("artifacts"), "expected a forecast chart artifact"

    print("\n--- Turn 2: report + email ---")
    mail_answer = ask(
        client,
        conversation_id,
        "Create a report summarizing the data analysis and email it to test@example.com",
    )
    print("answer:\n", mail_answer["content"])
    print("artifacts:", mail_answer.get("artifacts"))

    print("\nMAIL+FORECAST SMOKE TEST PASSED (see backend/scripts/received_mail/ for the sent email)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
