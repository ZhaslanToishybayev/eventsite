import os
import random
from rest_framework.authtoken.models import Token
from accounts.models import User
import resend


def generate_email_code(email: str, length: int = 6) -> str:
    code = ''.join(random.choices('0123456789', k=length))
    send_verification_email(email, code)
    return code


def send_verification_email(email: str, verification_code):
    resend.api_key = os.getenv("RESEND_API_KEY")

    params: resend.Emails.SendParams = {
        "from": "Центр событий <info@fan-club.kz>",
        "to": [email],
        "subject": "Код подтверждения для регистрации на сайте FAN-CLUB.KZ",
        "html": f"""
        <div style="font-family: Helvetica,Arial,sans-serif;min-width:1000px;overflow:auto;line-height:2">
            <div style="margin:50px auto;width:70%;padding:20px 0">
                <div style="border-bottom:1px solid #eee">
                    <a href="https://fan-club.kz" style="font-size:1.4em;color: #00466a;text-decoration:none;font-weight:600">Центр событий</a>
                </div>
                <p style="font-size:1.1em">Здравствуйте,</p>
                <p>Благодарим Вас за использование сайта Центр Событий. Используйте код ниже для завершения регистрации:</p>
                <h2 style="background: #00466a;margin: 0 auto;width: max-content;padding: 0 10px;color: #fff;border-radius: 4px;">{verification_code}</h2>
                <p style="font-size:0.9em;">Regards,<br />Центр событий</p>
                <hr style="border:none;border-top:1px solid #eee" />
                <div style="float:right;padding:8px 0;color:#aaa;font-size:0.8em;line-height:1;font-weight:300">
                    <p>Алматы, Казахстан</p>
                    <p>Instagram: @fan_club.kz</p>
                </div>
            </div>
        </div>""",
    }

    result = resend.Emails.send(params)
    
    if 'id' not in result:
        print(result)
        return

    print("Success: Email " + result['id'])
    return


def generate_token(user: User) -> dict:
    token = Token.objects.create(user=user)

    return {
        'token': str(token.key),
    }
