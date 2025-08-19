# serializers.py
try:
    from rest_framework.serializers import BaseSerializer  # noqa
except ImportError:
    pass
from typing import Dict, Optional, Tuple, Type, TypeVar, Union, cast

from adjango.aserializers import AModelSerializer

T = TypeVar("T", bound=AModelSerializer)


def dynamic_serializer(
    base_serializer: Type[T],
    include_fields: Tuple[str, ...],
    field_overrides: Optional[
        Dict[str, Union[Type[BaseSerializer], BaseSerializer]]
    ] = None,
) -> Type[T]:
    """
    Creates dynamic serializer based on base serializer,
    including specified fields and overriding some of them when needed.

    :param base_serializer: Base serializer class.
    :param include_fields: Tuple of field names to include.
    :param field_overrides: Dictionary with field overrides, where key is field name,
                            and value is serializer class or serializer instance.
    :return: New serializer class.
    """

    # Resolve model for Meta considering swappable User model
    resolved_model = None
    base_meta = getattr(base_serializer, "Meta", None)
    if base_meta is not None:
        resolved_model = getattr(base_meta, "model", None)
        try:
            # If base model is swappable AUTH_USER_MODEL, replace it with the actual user model
            if (
                resolved_model is not None
                and getattr(resolved_model._meta, "swappable", None)
                == "AUTH_USER_MODEL"
            ):
                from django.contrib.auth import get_user_model

                resolved_model = get_user_model()
        except Exception:
            # If anything goes wrong, fall back to the original model
            pass

    # Create new Meta class with needed fields (and possibly adjusted model)
    class Meta(base_serializer.Meta):  # type: ignore
        fields = include_fields
        if resolved_model is not None:
            model = resolved_model  # type: ignore

    # Attributes dictionary for new serializer
    attrs = {"Meta": Meta}

    # Store field overrides for later use
    field_overrides_to_apply = {}
    if field_overrides:
        for field_name, serializer in field_overrides.items():
            if isinstance(serializer, type) and issubclass(serializer, BaseSerializer):
                # If serializer class is passed, create its instance
                field_overrides_to_apply[field_name] = serializer(read_only=True)
            elif isinstance(serializer, BaseSerializer):
                # If serializer instance is passed, use it directly
                field_overrides_to_apply[field_name] = serializer
            else:
                raise ValueError(f"Invalid serializer for field '{field_name}'.")

    # Create custom __init__ that applies field overrides
    original_init = base_serializer.__init__

    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Apply field overrides after the fields are created
        for field_name, field_instance in field_overrides_to_apply.items():
            if hasattr(self, "fields") and field_name in self.fields:
                self.fields[field_name] = field_instance

    attrs["__init__"] = __init__

    # Create new serializer class
    dynamic_class = type("DynamicSerializer", (base_serializer,), attrs)

    # Cast type to Type[T] using cast
    return cast(Type[T], dynamic_class)
