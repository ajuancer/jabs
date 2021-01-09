# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Nil type metaclass."""

from .._plumtype import PlumType


class NilType(PlumType):

    """Nil type metaclass."""

    __nil_cls__ = None

    def __new__(mcs, name, bases, namespace):
        if mcs.__nil_cls__:
            raise TypeError("type 'Nil' is not an acceptable base type")

        mcs.__nil_cls__ = super().__new__(mcs, name, bases, namespace)
        mcs.__nil_cls__.__nil_instance__ = mcs.__nil_cls__()  # pylint: disable=not-callable
        return mcs.__nil_cls__

    def __call__(cls, value=None):
        try:
            nil = cls.__nil_instance__
        except AttributeError:
            nil = super().__call__()
            cls.__nil_instance__ = nil

        if (value is not None) and (value is not nil):
            raise TypeError("Nil() argument must be plum.nil or None")

        return nil
