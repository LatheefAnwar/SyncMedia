from celery import shared_task
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

BATCH_SIZE = 100

@shared_task
def send_email_campaign_mass_mail(subject, context, emails):
    print('email length',len(emails))
    email_batched = list(emails[i:i+BATCH_SIZE] for i in range(0,len(emails), BATCH_SIZE))
    print('email batched',email_batched)
    print('\n\n sending to for loop')
    for batch in email_batched:
        send_single_email.delay(subject, context, batch)
        print('\n\nbatch is ',batch)


@shared_task
def send_single_email(subject, context, email):
    html_content = render_to_string('emailcampaign.html', context)
    text_content = strip_tags(html_content)

    try:
        email_message = EmailMultiAlternatives(
            subject=subject,
            body= text_content,
            from_email= settings.EMAIL_HOST_USER,
            to=email
        )
        email_message.attach_alternative(html_content, 'text/html')
        email_message.send()
        logger.info(f"email send successfully to {email}")
    except Exception as e:
        logger.info(f'Error sending bulk emails: {e}')

    