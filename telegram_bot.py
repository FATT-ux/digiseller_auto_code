import requests
from config import TG_BOT_TOKEN, TG_CHAT_ID


def send_tg_notification(order_id: int, product_name: str, code: str):
    """Отправляет уведомление продавцу об успешной выдаче кода."""
    base = "https://" + "api.telegram.org" + "/bot"
    url = f"{base}{TG_BOT_TOKEN}/sendMessage"
    text = (
        f"✅ <b>Код успешно выдан!</b>\n\n"
        f"🧾 <b>Заказ №:</b> <code>{order_id}</code>\n"
        f"📦 <b>Товар:</b> {product_name}\n"
        f"🔑 <b>Выданный код:</b> <code>{code}</code>"
    )
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram] Ошибка отправки уведомления: {e}")
