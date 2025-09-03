from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import get_template
from celery import shared_task


@shared_task(name="send_email")
def send_email(template=None, subject="", recipient_email=None, cc_emails=None, bcc_emails=None, body_context=None,
               is_html=False):
    try:
        if not recipient_email:
            raise ValueError("Recipient email address is required.")

        sender_email = settings.EMAIL_HOST_USER

        if template:
            try:
                email_body = get_template(template).render(body_context)
            except Exception as e:
                print(f"Error rendering email template: {e}")
                raise ValueError("Invalid email template or context.")
        else:
            email_body = body_context.get("body", "") if body_context else ""

        email = EmailMessage(
            subject=subject,
            body=email_body,
            from_email=sender_email,
            to=recipient_email,
            cc=cc_emails,
            bcc=bcc_emails,
        )

        if is_html:
            email.content_subtype = "html"
        email.send()

        # Retrieve Message-ID
        message_id = email.message().get("Message-ID")
        print(f"Message-ID: {message_id}")

        return message_id  # Return the Message-ID if needed

    except Exception as e:
        print(f"Error sending email: {e}")
        return False