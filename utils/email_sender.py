import requests

def enviar_email_confirmacao(api_key, destino, assunto, html):
    """
    Envia um e-mail usando a API do Brevo (Sendinblue).
    """
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }

    payload = {
        "sender": {"name": "NextDrive", "email": "contatonextdrive@gmail.com"},
        "to": [{"email": destino}],
        "subject": assunto,
        "htmlContent": html
    }

    r = requests.post(url, headers=headers, json=payload)
    return r.status_code, r.text
