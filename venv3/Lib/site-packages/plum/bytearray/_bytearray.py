# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as a byte array."""

from .._plum import InsufficientMemoryError, Plum, getbytes
from ._bytearraytype import ByteArrayType


class ByteArray(bytearray, Plum, metaclass=ByteArrayType):

    """Interpret bytes as a byte array.

    .. code-block:: none

        ByteArray(iterable_of_ints) -> bytes array
        ByteArray(string, encoding[, errors]) -> bytes array
        ByteArray(bytes_or_buffer) -> mutable copy of bytes_or_buffer
        ByteArray(int) -> bytes array of size given by the parameter initialized with null bytes
        ByteArray() -> empty bytes array

    """

    # filled in by metaclass
    __nbytes__ = None
    __fill__ = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.__nbytes__ is not None:
            nbytes_short = self.__nbytes__ - len(self)

            if self.__fill__ is not None and nbytes_short > 0:
                self.extend(self.__fill__ * nbytes_short)

            elif nbytes_short:
                if nbytes_short < 0:
                    raise ValueError(
                        f'expected {self.__nbytes__} bytes, got {len(self)}')

                raise ValueError(
                    f'expected {self.__nbytes__} bytes, got {len(self)}, '
                    f'either supply the correct number of bytes or specify '
                    f'a fill value for the ByteArray subclass')

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump, *, nbytes=None):
        # pylint: disable=too-many-arguments,arguments-differ

        if nbytes is None:
            nbytes = cls.__nbytes__

        try:
            unpacked_bytes, offset = getbytes(buffer, offset, nbytes, dump)
        except InsufficientMemoryError:
            if dump:
                # getbytes() adds records in 16 byte chunks showing bytes it was able
                # to unpack, reassemble them as if operation was successful
                dump.memory = b''.join(subdump.memory for subdump in dump)
                del dump[:]
            raise
        finally:
            if dump:
                unpacked_bytes = dump.memory
                dump.memory = b''
                for i in range(0, len(unpacked_bytes), 16):
                    chunk = unpacked_bytes[i:i + 16]
                    dump.add_record(
                        access=f'[{i}:{i + len(chunk)}]',
                        value=str(bytearray(chunk)),
                        memory=chunk)

        return bytearray(unpacked_bytes), offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        nbytes = cls.__nbytes__

        if nbytes is None:
            nbytes = len(value)

        elif len(value) != nbytes:
            raise ValueError(
                f'expected length to be {nbytes} but instead found {len(value)}')

        end = offset + nbytes
        buffer[offset:end] = value

        if dump:
            for i in range(0, nbytes, 16):
                chunk = value[i:i + 16]
                dump.add_record(
                    access=f'[{i}:{i + len(chunk)}]',
                    value=str(bytearray(chunk)),
                    memory=chunk)

        return end

    def __repr__(self):
        return f"{type(self).__name__}({bytearray.__repr__(self).split('(', 1)[1][:-1]})"

    __str__ = __repr__  # needed for py3.6
