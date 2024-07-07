from app.core.config import settings


def test_send_emails_with_emails() -> None:
    import emails
    from emails.template import JinjaTemplate as T

    message = emails.html(subject='Test email',
                          html=T('<p>This is a test email</p>'),
                          mail_from=('sender', settings.SMTP_USER))

    r = message.send(to=('receiver', settings.EMAIL_TEST_USER),
                     smtp={'host': settings.SMTP_HOST, 'port': settings.SMTP_PORT, 'tls': True,
                           'user': settings.SMTP_USER, 'password': settings.SMTP_PASSWORD})
    assert r.status_code == 250


def test_send_emails_with_email() -> None:
    import smtplib

    msg = "hello world!"

    SMTP_USER = settings.SMTP_USER
    SMTP_PASSWORD = settings.SMTP_PASSWORD
    with smtplib.SMTP(host=settings.SMTP_HOST, port=settings.SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(settings.EMAILS_FROM_EMAIL, settings.EMAIL_TEST_USER, msg)
