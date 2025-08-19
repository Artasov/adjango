# test_tasks.py
from unittest.mock import MagicMock, patch

import pytest

from adjango.tasks import send_emails_task


class TestSendEmailsTask:
    """Tests for задачи send_emails_task"""

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_basic(self, mock_send_emails):
        """Test базовой функциональности задачи"""
        subject = "Test Subject"
        emails = ["test1@example.com", "test2@example.com"]
        template = "test_template.html"
        context = {"name": "John", "message": "Test message"}

        send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_with_tuple_emails(self, mock_send_emails):
        """Test задачи с tuple emails"""
        subject = "Test Subject"
        emails = ("test1@example.com", "test2@example.com")
        template = "test_template.html"
        context = {"data": "test"}

        send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_with_single_email(self, mock_send_emails):
        """Test задачи с одним email"""
        subject = "Single Email Test"
        emails = ["single@example.com"]
        template = "single_template.html"
        context = {"user": "test_user"}

        send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_empty_context(self, mock_send_emails):
        """Test задачи с пустым контекстом"""
        subject = "Empty Context Test"
        emails = ["test@example.com"]
        template = "empty_template.html"
        context = {}

        send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_exception_handling(self, mock_send_emails):
        """Test обработки исключений в задаче"""
        # Настраиваем мок для вызова исключения
        mock_send_emails.side_effect = Exception("Email sending failed")

        subject = "Exception Test"
        emails = ["test@example.com"]
        template = "error_template.html"
        context = {"error": "test"}

        # Задача должна поднять исключение для retry механизма Celery
        with pytest.raises(Exception, match="Email sending failed"):
            send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)

    def test_send_emails_task_function_exists(self):
        """Test что функция задачи существует и имеет правильные атрибуты"""
        # Проверяем, что это Celery задача
        assert hasattr(send_emails_task, "delay")
        assert hasattr(send_emails_task, "apply_async")
        assert callable(send_emails_task)

    def test_send_emails_task_retry_configuration(self):
        """Test конфигурации retry для задачи"""
        # Проверяем настройки retry
        task_meta = send_emails_task

        # Проверяем, что задача имеет retry настройки
        assert hasattr(task_meta, "autoretry_for")
        assert hasattr(task_meta, "retry_kwargs")

        # Проверяем конкретные значения retry
        if hasattr(task_meta, "autoretry_for"):
            assert Exception in task_meta.autoretry_for

        if hasattr(task_meta, "retry_kwargs"):
            retry_kwargs = task_meta.retry_kwargs
            assert retry_kwargs.get("max_retries") == 3
            assert retry_kwargs.get("countdown") == 20

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_type_annotations(self, mock_send_emails):
        """Test типов аргументов задачи"""
        # Проверяем, что функция принимает правильные типы
        subject = "Type Test"
        emails_list = ["test1@example.com", "test2@example.com"]
        emails_tuple = ("test1@example.com", "test2@example.com")
        template = "type_template.html"
        context = {"type": "test"}

        # Тест с list
        send_emails_task(subject, emails_list, template, context)

        # Тест с tuple
        send_emails_task(subject, emails_tuple, template, context)

        assert mock_send_emails.call_count == 2

    @patch("adjango.tasks.logging.getLogger")
    def test_logger_initialization(self, mock_get_logger):
        """Test инициализации логгера"""
        # Перезагружаем модуль для проверки инициализации логгера
        import importlib

        import adjango.tasks

        importlib.reload(adjango.tasks)

        # Логгер должен быть создан с именем модуля
        mock_get_logger.assert_called_with("adjango.tasks")

    @patch("adjango.tasks.send_emails")
    def test_send_emails_task_complex_context(self, mock_send_emails):
        """Test задачи со сложным контекстом"""
        subject = "Complex Context Test"
        emails = ["test@example.com"]
        template = "complex_template.html"
        context = {
            "user": {
                "name": "John Doe",
                "email": "john@example.com",
                "preferences": ["email", "sms"],
            },
            "data": [1, 2, 3, 4, 5],
            "metadata": {"timestamp": "2023-01-01T00:00:00Z", "version": "1.0"},
        }

        send_emails_task(subject, emails, template, context)

        mock_send_emails.assert_called_once_with(subject, emails, template, context)
