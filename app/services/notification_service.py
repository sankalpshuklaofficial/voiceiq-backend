from twilio.rest import Client
from app.core.config import settings

def get_twilio_client():
    return Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

async def send_sms(
    to_number: str,
    message: str
) -> dict:
    """
    Send SMS notification via Twilio
    """
    try:
        client = get_twilio_client()
        message = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number
        )
        return {
            "success": True,
            "message_sid": message.sid
        }
    except Exception as e:
        print(f"SMS Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def send_whatsapp(
    to_number: str,
    message: str
) -> dict:
    """
    Send WhatsApp notification via Twilio
    """
    try:
        client = get_twilio_client()
        message = client.messages.create(
            body=message,
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{to_number}"
        )
        return {
            "success": True,
            "message_sid": message.sid
        }
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def send_appointment_confirmation(
    customer_phone: str,
    customer_name: str,
    business_name: str,
    appointment_time: str,
    use_whatsapp: bool = False
) -> dict:
    """
    Send appointment confirmation to customer
    """
    message = f"""
Dear {customer_name},

Your appointment at {business_name} has been confirmed.
Date & Time: {appointment_time}

Please arrive 10 minutes early.
For any changes, please call us back.

Thank you!
    """.strip()

    if use_whatsapp:
        return await send_whatsapp(customer_phone, message)
    else:
        return await send_sms(customer_phone, message)