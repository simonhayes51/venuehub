import requests
from django.conf import settings

def verify_recaptcha(token: str) -> bool:
    secret = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
    if not secret:
        return True  # dev fallback
    try:
        resp = requests.post("https://www.google.com/recaptcha/api/siteverify",
                             data={"secret": secret, "response": token}, timeout=5)
        data = resp.json()
        return bool(data.get("success"))
    except Exception:
        return False
