# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Integer type view."""

from numbers import Integral

from .._plumview import NumberView


class IntView(NumberView, Integral):  # pylint: disable=too-many-ancestors

    """Integer type view."""

    def __and__(self, other):
        return self.get() & other

    def __getitem__(self, item):
        dref = self.__type__.__dref__

        if dref is None:
            raise RuntimeError(
                f'{self.__type__!r} type does not support pointer dereference')

        offset = self.get() + (item * dref.__nbytes__)

        return dref.view(self.__buffer__, offset)

    def __iand__(self, other):
        self.set(self.get() & other)
        return self

    def __ilshift__(self, other):
        self.set(self.get() << other)
        return self

    __int__ = NumberView.get

    def __invert__(self):
        return ~self.get()  # pylint: disable=invalid-unary-operand-type

    def __ior__(self, other):
        self.set(self.get() | other)
        return self

    def __irshift__(self, other):
        self.set(self.get() >> other)
        return self

    def __ixor__(self, other):
        self.set(self.get() ^ other)
        return self

    def __lshift__(self, other):
        return self.get() << other

    def __or__(self, other):
        return self.get() | other

    def __rand__(self, other):
        return other & self.get()

    def __rlshift__(self, other):
        return other << self.get()

    def __ror__(self, other):
        return other | self.get()

    def __rrshift__(self, other):
        return other >> self.get()

    def __rshift__(self, other):
        return self.get() >> other

    def __rxor__(self, other):
        return other ^ self.get()

    def __setitem__(self, item, value):
        dref_view = self.__getitem__(item)
        dref_view.set(value)

    def __xor__(self, other):
        return self.get() ^ other

    def to_bytes(self, length, byteorder, *, signed=False):
        """Return an array of bytes representing an integer.

        :param int length:
            Length of bytes object to use.  An OverflowError is raised if the
            integer is not representable with the given number of bytes.

        :param str byteorder:
            The byte order used to represent the integer.  If byteorder is 'big',
            the most significant byte is at the beginning of the byte array.  If
            byteorder is 'little', the most significant byte is at the end of the
            byte array.  To request the native byte order of the host system, use
            ``sys.byteorder`` as the byte order value.

        :param bool signed:
            Determines whether two's complement is used to represent the integer.
            If signed is False and a negative integer is given, an OverflowError
            is raised.

        :returns: array of bytes
        :rtype: bytes

        """
        return self.get().to_bytes(length, byteorder, signed=signed)
