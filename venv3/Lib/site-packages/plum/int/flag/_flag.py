# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Integer flag enumeration type."""

import enum
import sys

from ..._plum import getbytes
from .._int import Int
from ._flagtype import FlagType


class Flag(Int, enum.Flag, metaclass=FlagType):
    # pylint: disable=too-many-ancestors

    """Interpret bytes as an integer with bit flag enumerations.

    :param x: value
    :type x: number or str
    :param int base: base of x when x is ``str``

    """

    def __getattr__(self, name):
        try:
            member = type(self)[name.upper()]
        except KeyError:
            object.__getattribute__(self, name)
        # pylint: disable=protected-access
        return bool(self._value_ & member._value_)

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        nbytes = cls.__nbytes__

        try:
            value = cls(value)

            chunk = value.to_bytes(nbytes, cls.__byteorder__, signed=cls.__signed__)

            if dump:
                dump.value = value
                dump.memory = chunk
                cls._add_flags_to_dump(value, dump)

        except Exception:
            if dump:
                # use repr in case str or something that otherwise looks like an int
                dump.value = repr(value)
            raise

        end = offset + nbytes
        buffer[offset:end] = chunk

        return end

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        chunk, offset = getbytes(buffer, offset, cls.__nbytes__, dump)

        value = cls.from_bytes(chunk, cls.__byteorder__, signed=cls.__signed__)

        if dump:
            dump.value = value
            cls._add_flags_to_dump(value, dump)

        return value, offset

    @classmethod
    def _add_flags_to_dump(cls, value, dump):
        dump.value = int(value)

        for member in cls:
            dump.add_record(
                access='.' + member.name.lower(),
                bits=(int(member.bit_length() - 1), 1),
                value=str(bool(value & member)),
                cls=bool)

    _missing_ = classmethod(
        enum.IntFlag._missing_.__func__)  # pylint: disable=protected-access
    _create_pseudo_member_ = classmethod(
        enum.IntFlag._create_pseudo_member_.__func__)  # pylint: disable=protected-access

    __or__ = enum.IntFlag.__or__
    __and__ = enum.IntFlag.__and__
    __xor__ = enum.IntFlag.__xor__
    __invert__ = enum.Flag.__invert__

    __ror__ = enum.IntFlag.__ror__
    __rand__ = enum.IntFlag.__rand__
    __rxor__ = enum.IntFlag.__rxor__

    if sys.version_info < (3, 7):  # pragma: no cover
        def __repr__(self):
            enum_repr = enum.IntFlag.__repr__(self)
            if '(' in enum_repr:  # pragma: no cover
                beg, _, int_repr, _ = enum_repr.replace('(', ' ').replace(')', ' ').split()
                enum_repr = f'{beg} {int_repr}>'
            return enum_repr
    else:  # pragma: no cover
        def __repr__(self):
            return enum.IntFlag.__repr__(self)

    def __str__(self):
        return enum.IntFlag.__str__(self)
