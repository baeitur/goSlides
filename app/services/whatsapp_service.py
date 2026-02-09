"""WhatsApp notification integration (Twilio-compatible or generic webhook)."""
import os
import requests
from flask import current_app


def send_whatsapp_message(phone: str, message: str) -> bool:
    """
    Send a WhatsApp message. Supports:
    - Twilio: set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM (e.g. whatsapp:+14155238886)
    - Generic webhook: set WHATSAPP_WEBHOOK_URL (POST with json body { "phone": "...", "message": "..." })
    Returns True if sent successfully (or no provider configured and we skip).
    """
    phone = (phone or "").strip().replace(" ", "").replace("-", "")
    if not phone or not message:
        return False

    # Twilio
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_num = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    if sid and token:
        try:
            to = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone
            r = requests.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                auth=(sid, token),
                data={"From": from_num, "To": to, "Body": message},
                timeout=10,
            )
            if r.status_code in (200, 201):
                return True
            current_app.logger.warning("Twilio WhatsApp send failed: %s %s", r.status_code, r.text)
        except Exception as e:
            current_app.logger.warning("Twilio WhatsApp error: %s", e)
        return False

    # Generic webhook
    webhook = os.environ.get("WHATSAPP_WEBHOOK_URL")
    if webhook:
        try:
            r = requests.post(
                webhook,
                json={"phone": phone, "message": message},
                timeout=10,
            )
            if r.status_code in (200, 201, 204):
                return True
        except Exception as e:
            current_app.logger.warning("WhatsApp webhook error: %s", e)
        return False

    # No provider configured
    return False


def notify_registration_confirmation(registrant, activity):
    """Send WhatsApp to registrant after registration (if phone and integration configured)."""
    phone = (registrant.phone or "").strip()
    if not phone:
        return False
    message = (
        f"Hi {registrant.name}! You have registered for *{activity.title}* (Go Slides). "
        "We will verify your registration shortly."
    )
    return send_whatsapp_message(phone, message)
