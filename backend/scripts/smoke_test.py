import json
import sys
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_data"


def sse_events(response: httpx.Response):
    event_name = None
    for line in response.iter_lines():
        if line.startswith("event:"):
            event_name = line.split(":", 1)[1].strip()
        elif line.startswith("data:"):
            data = json.loads(line.split(":", 1)[1].strip())
            yield event_name, data


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=120)

    health = client.get("/api/health").json()
    print("health:", health)
    assert health["status"] == "ok"

    conversation = client.post("/api/conversations", json={"title": "Smoke test"}).json()
    conversation_id = conversation["id"]
    print("conversation:", conversation_id)

    for fname in ("sample.csv", "sample.pdf"):
        path = SAMPLE_DIR / fname
        with open(path, "rb") as f:
            resp = client.post(
                f"/api/conversations/{conversation_id}/files",
                files={"file": (fname, f, "application/octet-stream")},
            )
        resp.raise_for_status()
        print("uploaded:", resp.json())

    question = (
        "Using the uploaded documents and data: what does the refund policy say, "
        "and what are the key insights from the revenue data?"
    )
    seen_events = {"plan": False, "agent_status": False, "final": False}
    final_payload = None

    with client.stream(
        "POST", f"/api/conversations/{conversation_id}/chat", json={"message": question}
    ) as response:
        for event_name, data in sse_events(response):
            if event_name == "error":
                print("STREAM ERROR:", data)
                return 1
            if event_name in seen_events:
                seen_events[event_name] = True
            if event_name == "plan":
                print("plan:", data["plan"])
            if event_name == "agent_status":
                print("agent_status:", data)
            if event_name == "final":
                final_payload = data

    print("final answer:\n", final_payload["content"] if final_payload else None)
    print("citations:", final_payload.get("citations") if final_payload else None)
    print("artifacts:", final_payload.get("artifacts") if final_payload else None)

    assert seen_events["plan"], "No plan event received"
    assert seen_events["final"], "No final event received"
    assert final_payload and final_payload["content"], "Final answer was empty"

    if final_payload.get("artifacts"):
        artifact = final_payload["artifacts"][0]
        dl = client.get(f"/api/artifacts/{artifact['id']}/download")
        dl.raise_for_status()
        print(f"Downloaded artifact {artifact['id']}: {len(dl.content)} bytes")

    print("\nSMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
