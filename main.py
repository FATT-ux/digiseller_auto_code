import json
import os
import time
from config import CHECK_INTERVAL, DEFAULT_MAIL, PRODUCTS_MAIL_MAP
from digiseller_api import DigisellerClient
from mail_parser import fetch_latest_code
from telegram_bot import send_tg_notification

PROCESSED_FILE = "processed_msgs.json"


def load_processed_ids() -> set:
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(str(x) for x in json.load(f))
    return set()


def save_processed_ids(msg_ids: set):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(msg_ids), f)


def main():
    client = DigisellerClient()
    processed_msgs = load_processed_ids()
    print("Бот автовыдачи кодов запущен. Ожидание сообщений...")

    while True:
        try:
            unread_chats = client.get_unread_chats()
            if unread_chats:
                print(f"[Проверка] Найдено чатов: {len(unread_chats)}")

            for chat in unread_chats:
                order_id = chat.get("id_i") or chat.get("order_id")
                if not order_id:
                    continue

                messages = client.get_chat_messages(order_id)

                for msg in messages:
                    msg_id = str(msg["id"])
                    is_buyer = msg.get("buyer") in (1, True, "1") and not msg.get("admin")

                    # Пропускаем уже обработанные сообщения и сообщения от самого продавца
                    if msg_id in processed_msgs or not is_buyer:
                        continue

                    text = str(msg.get("message", "")).strip().lower()
                    print(f"[Заказ {order_id}] Новое сообщение от покупателя: {text}")

                    if "!код" in text:
                        print(f"[Заказ {order_id}] Получена команда !код")
                        order_info = client.get_order_info(order_id)

                        if not order_info or not order_info["is_paid"]:
                            client.send_message(
                                order_id,
                                "Ваш заказ еще не оплачен. Пожалуйста, завершите оплату и повторите команду !код."
                            )
                            print(f"[Заказ {order_id}] Заказ не оплачен.")
                        else:
                            product_id = order_info["product_id"]
                            mail_cfg = PRODUCTS_MAIL_MAP.get(product_id, DEFAULT_MAIL)

                            code = fetch_latest_code(mail_cfg)
                            if code:
                                client.send_message(
                                    order_id,
                                    f"Ваш код подтверждения: {code}\nСпасибо за покупку!"
                                )
                                print(f"[Заказ {order_id}] Код {code} отправлен.")
                                send_tg_notification(order_id, order_info["product_name"], code)
                            else:
                                client.send_message(
                                    order_id,
                                    "Письмо с кодом еще не поступило на почту. Подождите 15–30 секунд и напишите !код снова."
                                )
                                print(f"[Заказ {order_id}] Письмо с кодом не найдено.")

                    # Сохраняем ID сообщения, чтобы не ответить на него повторно
                    processed_msgs.add(msg_id)
                    save_processed_ids(processed_msgs)

                # Помечаем чат прочитанным после обработки всех сообщений
                client.mark_chat_seen(order_id)

        except Exception as e:
            print(f"[Ошибка в основном цикле]: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()

