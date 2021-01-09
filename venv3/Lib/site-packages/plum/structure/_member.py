# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Structure member definition."""

import operator
from types import FunctionType, MethodType

from .._plum import Plum, PlumType


def __pack__(cls, buffer, offset, parent, value, dump):
    value_cls = cls.__cls_factory__(parent)
    if dump:
        dump.cls = value_cls
    return value_cls.__pack__(buffer, offset, parent, value, dump)


def __unpack__(cls, buffer, offset, parent, dump):
    value_cls = cls.__cls_factory__(parent)
    if dump:
        dump.cls = value_cls
    return value_cls.__unpack__(buffer, offset, parent, dump)


class Member:

    """Structure member definition.

    :param Plum cls: member type (or factory function)
    :param object default: initial value when unspecified
    :param bool ignore: ignore member during comparisons
    :param function setter: callback when member set via setattr()

    """

    __slots__ = [
        'cls',
        'default',
        'ignore',
        'index',
        'name',
        'setter',
    ]

    def __init__(self, *, cls=None, default=None, ignore=False, setter=None):

        if cls is None or isinstance(cls, (PlumType, FunctionType, MethodType)):
            self.cls = cls
        elif isinstance(cls, property):
            self.cls = cls.fget
        else:
            raise TypeError("'cls' must be a Plum type or a factory function")

        if isinstance(default, property):
            self.default = default.fget
        else:
            self.default = default

        self.ignore = ignore
        self.setter = setter
        self.name = None  # assigned during structure class construction
        self.index = None  # assigned during structure class construction

    def finish_initialization(self, index, name, annotations):
        """Set member name and type.

        :param int index: member index
        :param str name: member name
        :param dict annotations: subclass type annotations

        """
        self.index = index

        if self.name is not None:
            raise TypeError(
                f"invalid structure member {name!r} definition, "
                f"{type(self).__name__}() instance can not be shared "
                f"between structure members")

        self.name = name

        if self.cls is None:
            cls = annotations.get(name, None)

            if cls is None:
                raise TypeError(
                    f"missing structure member {name!r} type, either specify a "
                    f"Plum type using the 'cls' argument or as a type annotation")

            if not isinstance(cls, PlumType):
                raise TypeError(
                    f"invalid structure member {name!r} type, specify a Plum type "
                    f"or a factory function using the 'cls' argument")

            self.cls = cls

        elif isinstance(self.cls, (FunctionType, MethodType)):
            namespace = {
                '__cls_factory__': self.cls,
                '__pack__': classmethod(__pack__),
                '__unpack__': classmethod(__unpack__),
            }

            self.cls = PlumType('Varies', (Plum,), namespace)

    def adjust_members(self, members):
        """Perform adjustment to other members.

        :param dict members: structure member definitions

        """

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """

    def get_accessor(self):
        """Member accessor.

        :returns: descriptor protocol accessor
        :rtype: Member or property

        """
        if self.setter is None:
            def setitem(self, value, i=self.index):
                self[i] = value
        else:
            setitem = self.setter

        return property(operator.itemgetter(self.index)).setter(setitem)
