from __future__ import annotations

import logging

from celery import shared_task

from adjango.utils.mail import send_emails

log = logging.getLogger(__name__)


@shared_task(autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 20})
def send_emails_task(subject: str, emails: tuple[str, ...] | list[str, ...], template: str, context: dict) -> None:
    send_emails(subject, emails, template, context)
