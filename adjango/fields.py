# fields.py
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

from django.db.models import ManyToManyField

from adjango.descriptors import AManyToManyDescriptor, AManyRelatedManager

if TYPE_CHECKING:
    from django.db.models import Model

_RM = TypeVar("_RM", bound="Model")


class AManyToManyField(ManyToManyField, Generic[_RM]):
    if TYPE_CHECKING:
        # When accessing the descriptor on a model instance, the related manager
        # should be aware of the concrete model type it manages.  Declaring the
        # descriptor as returning ``AManyRelatedManager[_RM]`` allows static type
        # checkers to properly infer the type of objects returned by methods like
        # ``aall`` or ``all``.  Without inheriting from ``Generic`` and
        # annotating this method, usages such as ``await order.products.aall()``
        # would resolve to ``list[_RM]`` instead of ``list[Product]``.
        def __get__(
            self, instance: "Model | None", owner: type | None = None
        ) -> AManyRelatedManager[_RM]: ...

    # ``ManyToManyField`` does not support generics out of the box.  By
    # subclassing ``Generic`` we enable expressions like
    # ``products: AManyToManyField[Product]`` in models, and type checkers will
    # propagate ``Product`` to the returned manager.  No runtime behaviour is
    # affected, so ``__class_getitem__`` is unnecessary.

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        # Replace the descriptor with our custom one
        setattr(cls, self.name, AManyToManyDescriptor(self.remote_field, reverse=False))
