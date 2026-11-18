import imaplib
import email
from email.header import decode_header
import re


def _decode_str(raw_value: str) -> str:
    """Декодирует заголовки письма (From, Subject)."""
    if not raw_value:
        return ""
    decoded_parts = decode_header(raw_value)
    result = []
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(encoding or "utf-8", errors="ignore"))
        else:
            result.append(part)
    return "".join(result)


def _extract_body(msg) -> str:
    """Извлекает текстовое содержимое письма (plain text или очищенный html)."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if content_type in ("text/plain", "text/html") and "attachment" not in disposition:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body += payload.decode(charset, errors="ignore") + "\n"
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            body = payload.decode(charset, errors="ignore")

    # Удаляем HTML-теги, если письмо пришло только в формате HTML
    clean_text = re.sub(r"<[^>]+>", " ", body)
    return re.sub(r"\s+", " ", clean_text).strip()


def fetch_latest_code(mail_cfg: dict) -> str | None:
    """Подключается к IMAP, находит последнее письмо от нужного сервиса и парсит код."""
    mail = imaplib.IMAP4_SSL(mail_cfg["imap_server"])
    try:
        mail.login(mail_cfg["login"], mail_cfg["password"])
        mail.select("INBOX")

        # Ищем письма от указанного отправителя
        status, messages = mail.search(None, f'(FROM "{mail_cfg["sender"]}")')
        if status != "OK" or not messages[0]:
            return None

        # Берем ID самого свежего письма (последнего в списке)
        latest_email_id = messages[0].split()[-1]
        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        if status != "OK":
            return None

        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = _decode_str(msg.get("Subject", ""))
        body = _extract_body(msg)
        full_text = f"{subject} {body}"

        # Ищем код по регулярному выражению из конфига
        match = re.search(mail_cfg["code_regex"], full_text)
        if match:
            return match.group(1)
        return None
    finally:
        try:
            mail.close()
            mail.logout()
        except Exception:
            pass
