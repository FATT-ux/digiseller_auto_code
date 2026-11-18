SELLER_ID = 123456  # Замените на ваш ID продавца
API_KEY = "ВАШ_API_КЛЮЧ_DIGISELLER"  

TG_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TG_CHAT_ID = "987654321"

DEFAULT_MAIL = {
    "imap_server": "imap.yandex.ru",
    "login": "default_acc@yandex.ru",
    "password": "пароль_приложения",
    "sender": "noreply@steampowered.com",  
    "code_regex": r"\b([A-Z0-9]{5})\b"    
}


PRODUCTS_MAIL_MAP = {
    3456789: {
        "imap_server": "imap.mail.ru",
        "login": "xbox_acc@mail.ru",
        "password": "пароль_приложения_mail",
        "sender": "://microsoft.com",
        "code_regex": r"\b(\d{6,7})\b"  
    },
    9876543: {
        "imap_server": "://gmail.com",
        "login": "epic_acc@gmail.com",
        "password": "пароль_приложения_gmail",
        "sender": "epicgames.com",
        "code_regex": r"\b(\d{6})\b"    
    }
}

CHECK_INTERVAL = 7  
