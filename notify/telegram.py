"""notify/telegram.py — send a message to Telegram via the Bot API."""
import os
import sys
import urllib.parse
import urllib.request


def send(text: str, token: str = None, chat_id: str = None) -> bool:
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id, "text": text, "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=20) as r:
            ok = r.status == 200
            print("Telegram sent" if ok else f"Telegram HTTP {r.status}")
            return ok
    except Exception as e:
        print(f"Telegram error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # quick test: python notify/telegram.py "hello"
    send(sys.argv[1] if len(sys.argv) > 1 else "test from gold-trading-system")
