import hashlib
import time
import requests
from config import SELLER_ID, API_KEY


class DigisellerClient:
    BASE_URL = "https://api.digiseller.com/api"

    def __init__(self):
        self.token = None
        self.token_expires_at = 0

    def get_token(self) -> str:
        """Получает новый токен или возвращает действующий."""
        if self.token and time.time() < self.token_expires_at:
            return self.token

        timestamp = int(time.time())
        sign_str = f"{API_KEY}{timestamp}"
        sign = hashlib.sha256(sign_str.encode("utf-8")).hexdigest()

        url = f"{self.BASE_URL}/apilogin"
        payload = {
            "seller_id": SELLER_ID,
            "timestamp": timestamp,
            "sign": sign
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("retval") != 0:
            raise RuntimeError(f"Ошибка авторизации Digiseller: {data.get('desc')}")

        self.token = data["token"]
        # Токен действует 120 минут, обновляем с запасом через 110 минут
        self.token_expires_at = time.time() + 110 * 60
        return self.token

    def get_unread_chats(self) -> list:
        """Возвращает список чатов, в которых есть непрочитанные сообщения."""
        token = self.get_token()
        url = f"{self.BASE_URL}/debates/v2/chats"
        params = {
            "token": token,
            "filter_new": 1,  # 1 = только чаты с непрочитанными сообщениями
            "pagesize": 50
        }
        resp = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=15)
        resp.raise_for_status()
        return resp.json().get("items", [])

    def get_chat_messages(self, order_id: int) -> list:
        """Получает список сообщений в конкретном заказе."""
        token = self.get_token()
        url = f"{self.BASE_URL}/debates/v2"
        params = {"token": token, "id_i": order_id}
        resp = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, list) else data.get("items", [])

    def mark_chat_seen(self, order_id: int):
        """Помечает сообщения в чате прочитанными."""
        token = self.get_token()
        url = f"{self.BASE_URL}/debates/v2/seen"
        params = {"token": token, "id_i": order_id}
        requests.post(url, params=params, headers={"Accept": "application/json"}, timeout=15)

    def send_message(self, order_id: int, text: str):
        """Отправляет сообщение покупателю в чат заказа."""
        token = self.get_token()
        url = f"{self.BASE_URL}/debates/v2/"
        params = {"token": token, "id_i": order_id}
        payload = {"message": text, "files": []}
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        resp = requests.post(url, params=params, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()

    def get_order_info(self, order_id: int) -> dict | None:
        """Проверяет статус оплаты и возвращает информацию о товаре по номеру заказа."""
        token = self.get_token()
        url = f"{self.BASE_URL}/purchase/info/{order_id}"
        params = {"token": token}
        resp = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if data.get("retval") != 0:
            return None

        content = data.get("content", {})
        is_paid = (
            str(content.get("payment_state", "")).lower() == "paid"
            or content.get("date_pay") is not None
        )
        return {
            "is_paid": is_paid,
            "product_id": content.get("item_id") or content.get("product_id"),
            "product_name": content.get("name", "Товар")
        }
