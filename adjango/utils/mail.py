# utils/mail.py
from __future__ import annotations

import json
import logging

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_emails(subject: str, emails: tuple[str, ...] | list[str, ...], template: str, context=None):
    """
    Отправляет email с использованием указанного шаблона.

    @param subject: Тема письма.
    @param emails: Список email-адресов получателей.
    @param template: Путь к шаблону письма.
    @param context: Контекст для рендеринга шаблона.
    """
    from adjango.conf import ADJANGO_EMAIL_LOGGER_NAME
    log = logging.getLogger(ADJANGO_EMAIL_LOGGER_NAME)
    if send_mail(
            subject=subject, message=str(json.dumps(context)),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=list(emails),
            html_message=render_to_string(template, context=context if context is not None else {})
    ):
        log.info(f'Successfully sent {template=} {emails=}')
    else:
        log.critical(f'Failed to send {template=} {emails=} {context=}')
