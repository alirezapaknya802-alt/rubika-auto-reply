import os
import time
import requests

TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is missing.")

API_BASE = f"https://botapi.rubika.ir/v3/{TOKEN}"

SITE_LINK = "https://velvety-shortbread-50f12d.netlify.app"
CHANNEL_LINK = "https://rubika.ir/joinc/FHACDGCI0XCGWJFLVVLHCPJLHVCVRWQC"

REPLY_TEXT = (
    "🎮 تورنومنت کالاف\n\n"
    f"🌐 سایت ثبت‌نام:\n{SITE_LINK}\n\n"
    f"📢 کانال روبیکا:\n{CHANNEL_LINK}"
)

session = requests.Session()

def api_call(method, payload=None):
    response = session.post(
        f"{API_BASE}/{method}",
        json=payload or {},
        timeout=35,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("status") not in (None, "OK", "ok"):
        print(f"API {method} response: {data}")
    return data

def main():
    offset_id = None
    print("Rubika tournament bot started.")
    while True:
        try:
            params = {"limit": 100}
            if offset_id:
                params["offset_id"] = offset_id

            result = api_call("getUpdates", params)
            body = result.get("data") or {}
            updates = body.get("updates") or []
            offset_id = body.get("next_offset_id") or offset_id

            for item in updates:
                update = item.get("update", item)
                if update.get("type") != "NewMessage":
                    continue

                message = update.get("new_message") or {}
                chat_id = update.get("chat_id")
                text = message.get("text")

                # Ignore empty messages and updates without a chat identifier.
                if not chat_id or text is None:
                    continue

                api_call("sendMessage", {
                    "chat_id": str(chat_id),
                    "text": REPLY_TEXT,
                })
                print("Replied to a message.")

            if not updates:
                time.sleep(2)

        except requests.RequestException as exc:
            print(f"Network/API error: {exc}")
            time.sleep(5)
        except (ValueError, TypeError, KeyError) as exc:
            print(f"Unexpected response format: {exc}")
            time.sleep(5)

if __name__ == "__main__":
    main()
