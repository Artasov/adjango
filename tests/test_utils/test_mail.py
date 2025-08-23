from unittest.mock import patch

from adjango.utils.mail import send_emails


def test_send_emails_success(settings):
    settings.EMAIL_HOST_USER = 'from@example.com'
    with (
        patch('adjango.utils.mail.send_mail', return_value=1) as send_mail_mock,
        patch('adjango.utils.mail.render_to_string', return_value='body'),
        patch('logging.getLogger') as get_logger,
    ):
        logger = get_logger.return_value
        assert send_emails('subj', ('to@example.com',), 'tmpl.html', {'a': 1})
        send_mail_mock.assert_called_once()
        logger.info.assert_called_once()


def test_send_emails_fail(settings):
    settings.EMAIL_HOST_USER = 'from@example.com'
    with (
        patch('adjango.utils.mail.send_mail', return_value=0) as send_mail_mock,
        patch('adjango.utils.mail.render_to_string', return_value='body'),
        patch('logging.getLogger') as get_logger,
    ):
        logger = get_logger.return_value
        assert not send_emails('subj', ('to@example.com',), 'tmpl.html', {'a': 1})
        send_mail_mock.assert_called_once()
        logger.critical.assert_called_once()
