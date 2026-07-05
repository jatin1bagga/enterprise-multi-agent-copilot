import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from smoke_test import BASE_URL, sse_events  # noqa: E402

import httpx  # noqa: E402


def ask(client: httpx.Client, conversation_id: str, message: str) -> str:
    final_payload = None
    with client.stream(
        "POST", f"/api/conversations/{conversation_id}/chat", json={"message": message}
    ) as response:
        for event_name, data in sse_events(response):
            if event_name == "error":
                raise RuntimeError(data)
            if event_name == "final":
                final_payload = data
    return final_payload["content"] if final_payload else ""


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=120)
    conversation = client.post("/api/conversations", json={"title": "Memory test"}).json()
    conversation_id = conversation["id"]
    print("conversation:", conversation_id)

    answer1 = ask(client, conversation_id, "My favorite number is 42. Just acknowledge that.")
    print("answer1:", answer1)

    answer2 = ask(client, conversation_id, "What is my favorite number that I just told you?")
    print("answer2:", answer2)

    messages = client.get(f"/api/conversations/{conversation_id}/messages").json()
    print(f"persisted {len(messages)} messages")
    assert len(messages) == 4, f"expected 4 messages (2 turns), got {len(messages)}"
    assert "42" in answer2, "Follow-up answer did not reference prior turn's context"

    print("\nMEMORY SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
