# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Plum view base class."""

from math import ceil, floor

from ._dump import Dump
from ._plum import _pack_with_format, unpack_from, pack
from ._plumtype import PlumType


class PlumView:

    """Plum view base class.

    :param PlumType plumtype: associated plum type
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
    :param int offset: byte offset

    """

    # instance attributes (set as class attributes for pylint)
    __type__ = ...
    __buffer__ = ...
    __offset__ = ...

    def __init__(self, plumtype, buffer, offset):
        if not isinstance(plumtype, PlumType):
            raise TypeError('invalid plumtype')

        object.__setattr__(self, "__type__", plumtype)
        object.__setattr__(self, "__buffer__", buffer)
        object.__setattr__(self, "__offset__", offset)

    def __repr__(self):
        try:
            value = self.get()
        except Exception:  # pylint: disable=broad-except
            value = f'<view at 0x{self.__offset__:x}>'
        else:
            value = f'<view at 0x{self.__offset__:x}: {value!r}>'
        return value

    def __str__(self):
        try:
            value = str(self.get())
        except Exception:  # pylint: disable=broad-except
            value = f'<view at 0x{self.__offset__:x}>'
        return value

    def cast(self, cls):
        """Create a new view of item's buffer bytes.

        :param PlumType cls: view type
        :returns: new view
        :rtype: cls
        """
        return cls.view(self.__buffer__, self.__offset__)

    @property
    def dump(self):
        """Packed bytes summary.

        :returns: summary table of view detailing bytes and layout
        :rtype: str

        """
        dump = Dump(offset=self.__offset__)
        # offset -> 0, parent -> None
        _pack_with_format(self.__type__, bytearray(), 0, (self,), {}, None, dump)
        return dump

    def get(self):
        """Unpack item from buffer bytes.

        :returns: unpacked item
        :rtype: object

        For example, the following unpacks an unsigned 8 bit integer from
        a bytes buffer:

            >>> from plum.int.little import UInt8
            >>> buffer = b'\x00\xff\x00'
            >>> value = UInt8.view(buffer, offset=1)
            >>> value.get()
            255

        """
        return unpack_from(self.__type__, self.__buffer__, self.__offset__)

    @property
    def nbytes(self):
        """Bytes buffer view size in bytes.

        :returns: size
        :rtype: int

        """
        plum_type = self.__type__
        nbytes = plum_type.__nbytes__

        # FUTURE - remove cover comment when views support variable sized types
        if nbytes is None:  # pragma: no cover
            nbytes = len(pack(plum_type, self))

        return nbytes

    def pack(self):
        """Pack value as bytes.

        :returns: bytes buffer
        :rtype: bytearray

        """
        return pack(self.__type__, self)

    def pack_and_dump(self):
        """Pack value as bytes and produce bytes summary.

        :returns: bytes buffer, packed bytes summary
        :rtype: bytearray, Dump

        """
        return self.__type__.pack_and_dump(self)

    def pack_into(self, buffer, offset):
        """Pack value as bytes into a buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
        :param int offset: start location within bytes buffer

        """
        self.__type__.pack_into(buffer, offset, self)

    def pack_into_and_dump(self, buffer, offset):
        """Pack value as bytes into a buffer and produce bytes summary.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
        :param int offset: start location within bytes buffer
        :returns: packed bytes summary
        :rtype: Dump

        """
        return self.__type__.pack_into_and_dump(buffer, offset, self)

    def set(self, value):
        """Pack value into bytes buffer.

        :param object value: new value

        For example:
            >>> from plum.int.little import UInt8
            >>> buffer = bytearray(b'\x00\x00\x00')
            >>> view = UInt8.view(buffer, offset=1)
            >>> view.set(1)
            >>> buffer
            bytearray(b'\x00\x01\x00')

        """
        membytes = pack(self.__type__, value)

        self.__buffer__[self.__offset__:self.__offset__ + len(membytes)] = membytes


class NumberView(PlumView):

    """Numeric view class."""

    def __abs__(self):
        return abs(self.get())

    def __add__(self, other):
        return self.get() + other

    def __divmod__(self, other):
        return divmod(self.get(), other)

    def __float__(self):
        return float(self.get())

    def __eq__(self, other):
        return self.get() == other

    def __ge__(self, other):
        return self.get() >= other

    def __gt__(self, other):
        return self.get() > other

    def __iadd__(self, other):
        self.set(self.get() + other)
        return self

    def __imod__(self, other):
        self.set(self.get() % other)
        return self

    def __imul__(self, other):
        self.set(self.get() * other)
        return self

    def __int__(self):
        return int(self.get())

    def __ipow__(self, other):
        self.set(self.get() ** other)
        return self

    def __isub__(self, other):
        self.set(self.get() - other)
        return self

    def __le__(self, other):
        return self.get() <= other

    def __lt__(self, other):
        return self.get() < other

    def __mod__(self, other):
        return self.get() % other

    def __mul__(self, other):
        return self.get() * other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __neg__(self):
        return -self.get()  # pylint: disable=invalid-unary-operand-type

    def __pos__(self):
        return +self.get()  # pylint: disable=invalid-unary-operand-type

    def __pow__(self, exponent):
        return self.get().__pow__(exponent)

    def __radd__(self, other):
        return other + self.get()

    def __rdivmod__(self, other):
        return divmod(other, self.get())

    def __repr__(self):
        try:
            value = self.get()
        except Exception:  # pylint: disable=broad-except
            rep = f'<view at 0x{self.__offset__:x}>'
        else:
            rep = f'<view at 0x{self.__offset__:x}: {self.__type__.__name__}({value})>'
        return rep

    def __rmod__(self, other):
        return other % self.get()

    def __rmul__(self, other):
        return other * self.get()

    def __rpow__(self, other):
        return other ** self.get()

    def __rsub__(self, other):
        return other - self.get()

    def __rtruediv__(self, other):
        return other / self.get()

    def __sub__(self, other):
        return self.get() - other

    def __truediv__(self, other):
        return self.get() / other

    def __ceil__(self):
        return ceil(self.get())

    def __floor__(self):
        return floor(self.get())

    def __floordiv__(self, other):
        return self.get().__floordiv__(other)

    def __rfloordiv__(self, other):
        return self.get().__rfloordiv__(other)

    def __round__(self, ndigits=None):
        return self.get().__round__(ndigits)

    def __trunc__(self):
        return self.get().__trunc__()
