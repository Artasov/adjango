import sys

import pytest

from adjango.utils.common import is_celery, traceback_str


def test_is_celery_false(monkeypatch):
    monkeypatch.delenv("IS_CELERY", raising=False)
    monkeypatch.setattr(sys, "argv", ["manage.py"])
    assert not is_celery()


def test_is_celery_true_env(monkeypatch):
    monkeypatch.setenv("IS_CELERY", "1")
    monkeypatch.setattr(sys, "argv", ["manage.py"])
    assert is_celery()


def test_traceback_str():
    try:
        1 / 0
    except Exception as e:
        tb = traceback_str(e)
    assert "ZeroDivisionError" in tb
