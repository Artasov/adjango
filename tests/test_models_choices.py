# test_models_choices.py
import pytest
from django.db.models import TextChoices

from adjango.models.choices import ATextChoices


class TestATextChoices:
    """Тесты для ATextChoices"""

    def test_atext_choices_inheritance(self):
        """Тест наследования от TextChoices"""
        assert issubclass(ATextChoices, TextChoices)

    def test_get_label_with_enum_member(self):
        """Тест get_label с Enum членом"""

        class TestChoices(ATextChoices):
            OPTION1 = "opt1", "Option 1"
            OPTION2 = "opt2", "Option 2"

        # Передаем сам enum член
        label = TestChoices.get_label(TestChoices.OPTION1)
        assert label == "Option 1"

        label = TestChoices.get_label(TestChoices.OPTION2)
        assert label == "Option 2"

    def test_get_label_with_value(self):
        """Тест get_label со значением"""

        class TestChoices(ATextChoices):
            ACTIVE = "active", "Active Status"
            INACTIVE = "inactive", "Inactive Status"
            PENDING = "pending", "Pending Status"

        # Передаем значение enum
        label = TestChoices.get_label("active")
        assert label == "Active Status"

        label = TestChoices.get_label("inactive")
        assert label == "Inactive Status"

        label = TestChoices.get_label("pending")
        assert label == "Pending Status"

    def test_get_label_with_invalid_value(self):
        """Тест get_label с невалидным значением"""

        class TestChoices(ATextChoices):
            VALID = "valid", "Valid Option"

        # Передаем невалидное значение
        label = TestChoices.get_label("invalid")
        assert label is None

        label = TestChoices.get_label("")
        assert label is None

        label = TestChoices.get_label(None)
        assert label is None

    def test_get_label_with_different_types(self):
        """Тест get_label с разными типами значений"""

        class TestChoices(ATextChoices):
            OPTION1 = "opt1", "Option 1"

        # Передаем разные типы
        label = TestChoices.get_label(123)
        assert label is None

        label = TestChoices.get_label([])
        assert label is None

        label = TestChoices.get_label({})
        assert label is None

    def test_get_label_empty_choices(self):
        """Тест get_label с пустыми choices"""

        class EmptyChoices(ATextChoices):
            pass

        label = EmptyChoices.get_label("anything")
        assert label is None

    def test_get_label_complex_choices(self):
        """Тест get_label со сложными choices"""

        class StatusChoices(ATextChoices):
            DRAFT = "draft", "Draft Document"
            REVIEW = "review", "Under Review"
            APPROVED = "approved", "Approved Document"
            PUBLISHED = "published", "Published Document"
            ARCHIVED = "archived", "Archived Document"

        # Проверяем все варианты
        test_cases = [
            ("draft", "Draft Document"),
            ("review", "Under Review"),
            ("approved", "Approved Document"),
            ("published", "Published Document"),
            ("archived", "Archived Document"),
        ]

        for value, expected_label in test_cases:
            label = StatusChoices.get_label(value)
            assert label == expected_label

    def test_get_label_with_unicode(self):
        """Тест get_label с unicode символами"""

        class UnicodeChoices(ATextChoices):
            RUSSIAN = "ru", "Русский"
            CHINESE = "cn", "中文"
            EMOJI = "emoji", "😊 Emoji"

        label = UnicodeChoices.get_label("ru")
        assert label == "Русский"

        label = UnicodeChoices.get_label("cn")
        assert label == "中文"

        label = UnicodeChoices.get_label("emoji")
        assert label == "😊 Emoji"

    def test_get_label_case_sensitivity(self):
        """Тест чувствительности к регистру"""

        class CaseChoices(ATextChoices):
            UPPER = "UPPER", "Upper Case"
            lower = "lower", "Lower Case"
            Mixed = "Mixed", "Mixed Case"

        # Точное совпадение
        assert CaseChoices.get_label("UPPER") == "Upper Case"
        assert CaseChoices.get_label("lower") == "Lower Case"
        assert CaseChoices.get_label("Mixed") == "Mixed Case"

        # Неточное совпадение должно вернуть None
        assert CaseChoices.get_label("upper") is None
        assert CaseChoices.get_label("LOWER") is None
        assert CaseChoices.get_label("mixed") is None

    def test_get_label_with_numbers_and_special_chars(self):
        """Тест get_label с числами и спецсимволами"""

        class SpecialChoices(ATextChoices):
            VERSION_1_0 = "v1.0", "Version 1.0"
            VERSION_2_0 = "v2.0", "Version 2.0"
            BETA_TEST = "beta-test", "Beta Test"
            UNDERSCORE = "test_value", "Test Value"

        assert SpecialChoices.get_label("v1.0") == "Version 1.0"
        assert SpecialChoices.get_label("v2.0") == "Version 2.0"
        assert SpecialChoices.get_label("beta-test") == "Beta Test"
        assert SpecialChoices.get_label("test_value") == "Test Value"

    def test_get_label_method_return_type(self):
        """Тест типа возвращаемого значения"""

        class TestChoices(ATextChoices):
            OPTION = "opt", "Option Label"

        # Валидное значение должно вернуть строку
        label = TestChoices.get_label("opt")
        assert isinstance(label, str)
        assert label == "Option Label"

        # Невалидное значение должно вернуть None
        label = TestChoices.get_label("invalid")
        assert label is None

    def test_get_label_preserves_original_functionality(self):
        """Тест что оригинальная функциональность TextChoices сохранена"""

        class TestChoices(ATextChoices):
            OPTION1 = "opt1", "Option 1"
            OPTION2 = "opt2", "Option 2"

        # Проверяем что стандартные методы TextChoices работают
        assert TestChoices.OPTION1.value == "opt1"
        assert TestChoices.OPTION1.label == "Option 1"
        assert TestChoices.OPTION2.value == "opt2"
        assert TestChoices.OPTION2.label == "Option 2"

        # Проверяем choices
        choices_list = TestChoices.choices
        expected_choices = [("opt1", "Option 1"), ("opt2", "Option 2")]
        assert choices_list == expected_choices
