# test_middleware.py
import json
import logging
from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.http import HttpResponse

from adjango.middleware import (
    IPAddressMiddleware,
    MediaDomainSubstitutionJSONMiddleware,
)


class TestIPAddressMiddleware:
    """Tests for IPAddressMiddleware"""

    def setup_method(self):
        """Setup for each test"""
        self.get_response = MagicMock(return_value=HttpResponse("OK"))
        self.middleware = IPAddressMiddleware(self.get_response)

    def test_init(self):
        """Test initialization of middleware"""
        assert self.middleware.get_response == self.get_response

    @patch("adjango.middleware.ADJANGO_IP_LOGGER", "test_logger")
    @patch("adjango.middleware.logging.getLogger")
    def test_call_with_logging(self, mock_get_logger):
        """Test calling middleware с логированием"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        request = MagicMock()
        request.META = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1",
            "HTTP_X_REAL_IP": "10.0.0.1",
            "REMOTE_ADDR": "127.0.0.1",
        }

        response = self.middleware(request)

        assert response.status_code == 200
        assert request.ip == "192.168.1.1"
        assert mock_logger.warning.call_count == 3

    def test_call_without_logging(self):
        """Test calling middleware без логирования"""
        with patch("adjango.middleware.ADJANGO_IP_LOGGER", None):
            request = MagicMock()
            request.META = {
                "HTTP_X_FORWARDED_FOR": "192.168.1.1, 192.168.1.2",
                "HTTP_X_REAL_IP": "10.0.0.1",
                "REMOTE_ADDR": "127.0.0.1",
            }

            response = self.middleware(request)

            assert response.status_code == 200
            assert request.ip == "192.168.1.1"  # Первый IP из списка

    def test_ip_priority_forwarded_for(self):
        """Test приоритета HTTP_X_FORWARDED_FOR"""
        request = MagicMock()
        request.META = {
            "HTTP_X_FORWARDED_FOR": "192.168.1.1",
            "HTTP_X_REAL_IP": "10.0.0.1",
            "REMOTE_ADDR": "127.0.0.1",
        }

        self.middleware(request)

        assert request.ip == "192.168.1.1"

    def test_ip_priority_real_ip(self):
        """Test приоритета HTTP_X_REAL_IP когда нет FORWARDED_FOR"""
        request = MagicMock()
        request.META = {"HTTP_X_REAL_IP": "10.0.0.1", "REMOTE_ADDR": "127.0.0.1"}

        self.middleware(request)

        assert request.ip == "10.0.0.1"

    def test_ip_priority_remote_addr(self):
        """Test использования REMOTE_ADDR когда нет других"""
        request = MagicMock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        self.middleware(request)

        assert request.ip == "127.0.0.1"

    def test_ip_none_when_no_headers(self):
        """Test установки None когда нет IP заголовков"""
        request = MagicMock()
        request.META = {}

        self.middleware(request)

        assert request.ip is None

    def test_custom_ip_meta_name_forwarded_for(self):
        """Test кастомного IP мета имени с FORWARDED_FOR"""
        with patch("adjango.middleware.ADJANGO_IP_META_NAME", "HTTP_X_FORWARDED_FOR"):
            request = MagicMock()
            request.META = {"HTTP_X_FORWARDED_FOR": "192.168.1.1, 192.168.1.2"}

            self.middleware(request)

            assert request.ip == "192.168.1.1"
            assert request.META["REMOTE_ADDR"] == "192.168.1.1"

    def test_custom_ip_meta_name_other(self):
        """Test кастомного IP мета имени с другим заголовком"""
        with patch("adjango.middleware.ADJANGO_IP_META_NAME", "HTTP_X_CUSTOM_IP"):
            request = MagicMock()
            request.META = {"HTTP_X_CUSTOM_IP": "203.0.113.1"}

            self.middleware(request)

            assert request.ip == "203.0.113.1"
            assert request.META["REMOTE_ADDR"] == "203.0.113.1"

    def test_custom_ip_meta_name_not_present(self):
        """Test когда кастомный заголовок не присутствует"""
        with patch("adjango.middleware.ADJANGO_IP_META_NAME", "HTTP_X_MISSING"):
            request = MagicMock()
            request.META = {"REMOTE_ADDR": "127.0.0.1"}

            self.middleware(request)

            assert request.ip == "127.0.0.1"
            # REMOTE_ADDR не должен быть изменен
            assert request.META["REMOTE_ADDR"] == "127.0.0.1"


class TestMediaDomainSubstitutionJSONMiddleware:
    """Tests for MediaDomainSubstitutionJSONMiddleware"""

    def setup_method(self):
        """Setup for each test"""
        self.get_response = MagicMock()

    def test_init_with_media_settings(self):
        """Test initialization of с настройками media"""
        with patch.object(settings, "MEDIA_URL", "/media/"):
            with patch(
                "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
            ):
                middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

                assert middleware.media_url == "/media/"
                assert middleware.media_domain == "https://cdn.example.com"

    def test_init_without_base_logger(self):
        """Test initialization of без базового логгера"""
        with patch("adjango.middleware.ADJANGO_BASE_LOGGER", None):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)
            assert middleware.log is None

    def test_call_without_media_domain_raises_error(self):
        """Test ошибки при отсутствии MEDIA_SUBSTITUTION_URL"""
        with patch("adjango.middleware.MEDIA_SUBSTITUTION_URL", None):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

            response = HttpResponse(
                json.dumps({"test": "data"}), content_type="application/json"
            )
            self.get_response.return_value = response

            request = MagicMock()

            with pytest.raises(ValueError, match="settings.MEDIA_SUBSTITUTION_URL"):
                middleware(request)

    def test_call_non_json_response(self):
        """Test с не-JSON ответом"""
        with patch(
            "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
        ):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

            response = HttpResponse("<html>Test</html>", content_type="text/html")
            self.get_response.return_value = response

            request = MagicMock()
            result = middleware(request)

            assert result == response
            assert b"<html>Test</html>" in result.content

    def test_call_empty_json_response(self):
        """Test с пустым JSON ответом"""
        with patch(
            "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
        ):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

            response = HttpResponse("", content_type="application/json")
            self.get_response.return_value = response

            request = MagicMock()
            result = middleware(request)

            assert result == response

    def test_call_json_with_media_url_replacement(self):
        """Test замены media URL в JSON"""
        with patch.object(settings, "MEDIA_URL", "/media/"):
            with patch(
                "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
            ):
                middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

                original_data = {
                    "image": "/media/images/avatar.jpg",
                    "document": "/media/docs/file.pdf",
                    "other_url": "/static/css/style.css",
                }

                response = HttpResponse(
                    json.dumps(original_data), content_type="application/json"
                )
                self.get_response.return_value = response

                request = MagicMock()
                result = middleware(request)

                result_data = json.loads(result.content.decode("utf-8"))

                assert (
                    result_data["image"]
                    == "https://cdn.example.com/media/images/avatar.jpg"
                )
                assert (
                    result_data["document"]
                    == "https://cdn.example.com/media/docs/file.pdf"
                )
                assert (
                    result_data["other_url"] == "/static/css/style.css"
                )  # Не должно измениться

    def test_call_json_with_nested_structures(self):
        """Test замены в вложенных структурах"""
        with patch.object(settings, "MEDIA_URL", "/media/"):
            with patch(
                "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
            ):
                middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

                original_data = {
                    "user": {"avatar": "/media/avatars/user1.jpg", "name": "John"},
                    "images": [
                        "/media/gallery/img1.jpg",
                        "/media/gallery/img2.jpg",
                        "/static/default.jpg",
                    ],
                }

                response = HttpResponse(
                    json.dumps(original_data), content_type="application/json"
                )
                self.get_response.return_value = response

                request = MagicMock()
                result = middleware(request)

                result_data = json.loads(result.content.decode("utf-8"))

                assert (
                    result_data["user"]["avatar"]
                    == "https://cdn.example.com/media/avatars/user1.jpg"
                )
                assert result_data["user"]["name"] == "John"
                assert (
                    result_data["images"][0]
                    == "https://cdn.example.com/media/gallery/img1.jpg"
                )
                assert (
                    result_data["images"][1]
                    == "https://cdn.example.com/media/gallery/img2.jpg"
                )
                assert result_data["images"][2] == "/static/default.jpg"

    @patch("adjango.middleware.ADJANGO_BASE_LOGGER", "test_logger")
    @patch("adjango.middleware.logging.getLogger")
    def test_call_json_parsing_error_with_logging(self, mock_get_logger):
        """Test обработки ошибки парсинга JSON с логированием"""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        with patch(
            "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
        ):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

            response = HttpResponse("invalid json{", content_type="application/json")
            self.get_response.return_value = response

            request = MagicMock()
            result = middleware(request)

            assert result == response
            mock_logger.exception.assert_called_once()

    def test_replace_media_urls_string(self):
        """Test замены URL в строке"""
        with patch.object(settings, "MEDIA_URL", "/media/"):
            with patch(
                "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
            ):
                middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

                result = middleware._replace_media_urls("/media/test.jpg")
                assert result == "https://cdn.example.com/media/test.jpg"

                result = middleware._replace_media_urls("/static/test.css")
                assert result == "/static/test.css"

    def test_replace_media_urls_non_string(self):
        """Test обработки не-строковых типов"""
        with patch(
            "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
        ):
            middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

            assert middleware._replace_media_urls(123) == 123
            assert middleware._replace_media_urls(None) is None
            assert middleware._replace_media_urls(True) is True

    def test_content_length_update(self):
        """Test обновления Content-Length после замены"""
        with patch.object(settings, "MEDIA_URL", "/media/"):
            with patch(
                "adjango.middleware.MEDIA_SUBSTITUTION_URL", "https://cdn.example.com"
            ):
                middleware = MediaDomainSubstitutionJSONMiddleware(self.get_response)

                original_data = {"image": "/media/test.jpg"}

                response = HttpResponse(
                    json.dumps(original_data), content_type="application/json"
                )
                self.get_response.return_value = response

                request = MagicMock()
                result = middleware(request)

                assert result["Content-Length"] == str(len(result.content))
