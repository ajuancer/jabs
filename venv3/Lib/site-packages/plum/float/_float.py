# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as a floating point number."""

from struct import Struct

from .._plum import Plum, getbytes
from ._floattype import FloatType
from ._floatview import FloatView


class Float(float, Plum, metaclass=FloatType):

    """Interpret bytes as a floating point number.

    :param x: value
    :type x: number or str

    """

    __byteorder__ = 'little'
    __nbytes__ = 4
    __struct_pack__ = Struct('<f').pack
    __struct_unpack__ = Struct('<f').unpack

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        chunk, offset = getbytes(buffer, offset, cls.__nbytes__, dump)

        self = cls.__struct_unpack__(chunk)[0]

        if dump:
            dump.value = self

        return self, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        chunk = cls.__struct_pack__(value)

        end = offset + cls.__nbytes__
        buffer[offset:end] = chunk

        if dump:
            dump.value = value
            dump.memory = chunk

        return end

    @classmethod
    def __view__(cls, buffer, offset=0):
        """Create plum view of bytes buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
        :param int offset: byte offset

        """
        return FloatView(cls, buffer, offset)

    # override for consistency between python versions
    def __repr__(self):
        return f'{type(self).__name__}({float(self)})'

    # override for consistency between python versions
    def __str__(self):  # for py3.8+
        return f'{float(self)}'
