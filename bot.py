# bot.py
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_message(text: str) -> bool:
    """
    Envía un mensaje de texto al chat configurado.
    Devuelve True si se envió OK, False si hubo error o faltan credenciales.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("[bot] Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
        return False
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        if not resp.ok:
            print("[bot] Error al enviar:", resp.status_code, resp.text)
        return resp.ok
    except Exception as e:
        print("[bot] Excepción al enviar:", e)
        return False
