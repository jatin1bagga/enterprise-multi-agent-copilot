import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aiosmtpd.controller import Controller
from aiosmtpd.handlers import Message as MessageHandler

OUTPUT_DIR = Path(__file__).resolve().parent / "received_mail"


class SaveToDiskHandler(MessageHandler):
    def handle_message(self, message):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        count = len(list(OUTPUT_DIR.glob("*.eml")))
        path = OUTPUT_DIR / f"mail_{count + 1}.eml"
        path.write_bytes(message.as_bytes())
        print(f"Received email -> {path} (subject: {message['Subject']!r}, to: {message['To']!r})")


async def main():
    controller = Controller(SaveToDiskHandler(), hostname="localhost", port=1025)
    controller.start()
    print("Debug SMTP server listening on localhost:1025. Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        controller.stop()


if __name__ == "__main__":
    asyncio.run(main())
