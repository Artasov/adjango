# testing.py
import json

from asgiref.sync import sync_to_async

try:
    import pytest  # noqa
    from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED  # noqa
    from rest_framework.test import APIClient  # noqa
except ImportError:
    pass


class AsyncTestAPIClient:
    """
    Легкая обертка над APIClient, позволяющая вызывать методы асинхронно и
    компактно обрабатывать status_code, message и detail в ответах.
    """

    def __init__(self, user=None):
        self._client = APIClient()
        if user:
            self._client.force_authenticate(user=user)

    async def apost(self, url, data=None, expected_status=HTTP_201_CREATED, format='json', **kwargs):
        response = await sync_to_async(self._client.post)(url, data=data, format=format, **kwargs)
        self._handle_fail_if_not_expected(response, expected_status)
        return response

    async def aget(self, url, expected_status=HTTP_200_OK, format='json', **kwargs):
        response = await sync_to_async(self._client.get)(url, format=format, **kwargs)
        self._handle_fail_if_not_expected(response, expected_status)
        return response

    async def aput(self, url, data=None, expected_status=HTTP_200_OK, format='json', **kwargs):
        response = await sync_to_async(self._client.put)(url, data=data, format=format, **kwargs)
        self._handle_fail_if_not_expected(response, expected_status)
        return response

    async def apatch(self, url, data=None, expected_status=HTTP_200_OK, format='json', **kwargs):
        response = await sync_to_async(self._client.patch)(url, data=data, format=format, **kwargs)
        self._handle_fail_if_not_expected(response, expected_status)
        return response

    async def adelete(self, url, expected_status=HTTP_200_OK, format='json', **kwargs):
        response = await sync_to_async(self._client.delete)(url, format=format, **kwargs)
        self._handle_fail_if_not_expected(response, expected_status)
        return response

    @staticmethod
    def _handle_fail_if_not_expected(response, expected_status):
        """
        Если статус не совпал с ожидаемым – пытаемся вытащить detail/message,
        чтобы упасть с понятным сообщением, и вызываем pytest.fail().
        """
        if response.status_code != expected_status:
            try:
                if response.data and response.data.get('message'):
                    pytest.fail(
                        f"{response.data.get('message')} "
                        f"Status: {response.status_code}"
                    )
                error_response = json.loads(response.content)
                error_detail = error_response.get('detail', 'No detail provided')
            except (json.JSONDecodeError, AttributeError):
                error_detail = response.content.decode()
            pytest.fail(
                f"Expected: {expected_status}, got: {response.status_code}. "
                f"Detail: {error_detail}"
            )
