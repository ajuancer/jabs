# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Bytes buffer."""

from ._dump import Dump
from ._exceptions import ExcessMemoryError, ImplementationError
from ._plum import _unpack


class Buffer:

    """Bytes buffer."""

    def __init__(self, buffer):
        self.buffer = buffer
        self.offset = 0

    def unpack(self, fmt):
        r"""Unpack item(s) from this bytes buffer.

        :param fmt: plum type, tuple of types, or dict of types
        :type fmt: Plum, tuple of Plum, or dict
        :returns: unpacked item(s)
        :rtype: Plum, tuple of Plum, or dict of Plum (dependent on ``fmt``)
        :raises: ``UnpackError`` if insufficient bytes or value error

        For example:
            >>> from plum import Buffer
            >>> from plum.int.little import UInt8
            >>> membytes = Buffer(b'\x01\x02\x03\x04\x05')
            >>> membytes.unpack(UInt8)
            1
            >>> membytes.unpack((UInt8, UInt8))
            (2, 3)
            >>> membytes.unpack({'a': UInt8, 'b': UInt8})
            {'a': 4, 'b': 5}

        """
        try:
            # _unpack(fmt, buffer, offset, prohibit_excess, dump)
            items, self.offset = _unpack(fmt, self.buffer, self.offset, False, None)
        except Exception:
            # do it over to include dump in exception message
            _unpack(fmt, self.buffer, self.offset, False, Dump())
            raise ImplementationError()  # pragma: no cover

        return items

    def unpack_and_dump(self, fmt):
        r"""Unpack item(s) from this bytes buffer and produce a packed bytes summary.

        :param fmt: plum type, tuple of types, or dict of types
        :type fmt: Plum, tuple of Plum, or dict
        :returns: unpacked items
        :rtype: Plum, tuple of Plum, or dict of Plum (dependent on ``fmt``)
        :raises: ``UnpackError`` if insufficient bytes or value error

        For example:
            >>> from plum import Buffer
            >>> from plum.int.little import UInt8
            >>> membytes = Buffer(b'\x01\x02\x03\x04\x05')
            >>> value, dump = membytes.unpack_and_dump(UInt8)
            >>> value
            1
            >>> dump()
            +--------+-------+-------+-------+
            | Offset | Value | Bytes | Type  |
            +--------+-------+-------+-------+
            | 0      | 1     | 01    | UInt8 |
            +--------+-------+-------+-------+
            >>> value, dump = membytes.unpack_and_dump((UInt8, UInt8))
            >>> value
            (2, 3)
            >>> dump()
            +--------+--------+-------+-------+-------+
            | Offset | Access | Value | Bytes | Type  |
            +--------+--------+-------+-------+-------+
            | 0      | [0]    | 2     | 02    | UInt8 |
            | 1      | [1]    | 3     | 03    | UInt8 |
            +--------+--------+-------+-------+-------+
            >>> value, dump = membytes.unpack_and_dump({'a': UInt8, 'b': UInt8})
            >>> value
            {'a': 4, 'b': 5}
            >>> dump()
            +--------+--------+-------+-------+-------+
            | Offset | Access | Value | Bytes | Type  |
            +--------+--------+-------+-------+-------+
            | 0      | ['a']  | 4     | 04    | UInt8 |
            | 1      | ['b']  | 5     | 05    | UInt8 |
            +--------+--------+-------+-------+-------+

        """
        dump = Dump()
        items, self.offset = _unpack(fmt, self.buffer, self.offset, False, dump)
        return items, dump

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:  # don't check if already an exception
            extra_bytes = self.buffer[self.offset:]

            if extra_bytes:
                msg = f'{len(extra_bytes)} unconsumed bytes '
                raise ExcessMemoryError(msg, extra_bytes)
