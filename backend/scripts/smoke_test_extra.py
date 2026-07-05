import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from smoke_test import BASE_URL, SAMPLE_DIR, sse_events  # noqa: E402

import httpx  # noqa: E402


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=180)

    conversation = client.post("/api/conversations", json={"title": "Smoke test extra"}).json()
    conversation_id = conversation["id"]
    print("conversation:", conversation_id)

    with open(SAMPLE_DIR / "sample.csv", "rb") as f:
        resp = client.post(
            f"/api/conversations/{conversation_id}/files",
            files={"file": ("sample.csv", f, "text/csv")},
        )
    resp.raise_for_status()
    print("uploaded:", resp.json())

    question = (
        "Write and run python code to plot total revenue by region as a bar chart. "
        "Then generate a PDF and PowerPoint report summarizing the findings."
    )

    final_payload = None
    with client.stream(
        "POST", f"/api/conversations/{conversation_id}/chat", json={"message": question}
    ) as response:
        for event_name, data in sse_events(response):
            if event_name == "error":
                print("STREAM ERROR:", data)
                return 1
            if event_name == "plan":
                print("plan:", data["plan"])
            if event_name == "agent_status":
                print("agent_status:", data)
            if event_name == "final":
                final_payload = data

    print("\nfinal answer:\n", final_payload["content"] if final_payload else None)
    print("artifacts:", final_payload.get("artifacts") if final_payload else None)

    assert final_payload and final_payload["content"]
    artifacts = final_payload.get("artifacts") or []
    assert artifacts, "Expected at least one artifact (plot/report)"

    for artifact in artifacts:
        dl = client.get(f"/api/artifacts/{artifact['id']}/download")
        dl.raise_for_status()
        print(f"Downloaded {artifact['type']} ({artifact['title']}): {len(dl.content)} bytes")

    print("\nEXTRA SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
