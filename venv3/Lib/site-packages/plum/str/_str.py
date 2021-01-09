# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as a string."""

import codecs

from .. import InsufficientMemoryError
from .._plum import Plum, getbytes
from ._strtype import StrType


def _decode_str_bytes(buffer, decoder, zipped_char_bytes, zero_termination=False):
    reset = True
    for i, byte in enumerate(buffer):
        if reset:
            char_bytes = []
            zipped_char_bytes.append(['', char_bytes])
            reset = False

        if zero_termination and byte == 0:
            break

        char = decoder.decode(buffer[i:i + 1])
        char_bytes.append(byte)

        if char:
            zipped_char_bytes[-1][0] = char
            reset = True

    # FUTURE - test this
    # raise exception if bytes remain in decoder (character not complete)
    decoder.decode(b'', final=True)


def _encode_str_bytes(string, encoder, zipped_char_bytes):
    for char in string:
        zipped_char_bytes.append((char, encoder.encode(char)))

    assert not encoder.encode('', final=True)


def _iter_str_rows(zipped_char_bytes):
    row_index = 0
    row_chars, row_bytes = [], []

    for char, char_bytes in zipped_char_bytes:
        if len(char_bytes) + len(row_bytes) > 16:
            yield row_index, ''.join(row_chars), bytearray(row_bytes)
            row_index += len(row_chars)
            row_chars, row_bytes = [], []

        row_chars.append(char)
        row_bytes += char_bytes

    if row_bytes:
        yield row_index, ''.join(row_chars), bytearray(row_bytes)
    else:
        yield row_index, '', bytearray()


def _add_str_rows_to_dump(dump, zipped_char_bytes, buffer=None, string=None):
    nbytes = 0
    nchar = 0
    for index, chars, bytes_ in _iter_str_rows(zipped_char_bytes):
        dump.add_record(access=f'[{index}:{index + len(chars)}]', value=repr(chars), memory=bytes_)
        nbytes += len(bytes_)
        nchar += len(chars)

    if buffer:
        dump.add_extra_bytes('--error--', buffer[nbytes:])

    if string:
        string = string[nchar:]
        access = '--error--'
        for i in range(0, len(string), 16):
            dump.add_record(access).value = repr(string[i:i + 16])
            access = ''


def _add_str_bytes_to_dump(dump, buffer, decoder):
    zipped_char_bytes = []
    try:
        _decode_str_bytes(buffer, decoder, zipped_char_bytes)
    finally:
        _add_str_rows_to_dump(dump, zipped_char_bytes, buffer=buffer)


def _add_str_value_to_dump(dump, string, encoder):
    zipped_char_bytes = []
    try:
        _encode_str_bytes(string, encoder, zipped_char_bytes)
    finally:
        _add_str_rows_to_dump(dump, zipped_char_bytes, string=string)


class Str(str, Plum, metaclass=StrType):

    """Interpret bytes as a string.

    .. code-block:: none

        Str(object='') -> Str
        Str(bytes_or_buffer[, encoding[, errors]]) -> Str
        pack(Str, str) -> bytes
        unpack(Str, bytes_or_buffer) -> Str

    :param object: string like object
    :type object: object or bytes or buffer
    :param str encoding: encoding name (see :mod:`codecs` standard encodings)
    :param str error: (e.g. ``'string'``, ``'ignore'``, ``'replace'``)

    """

    # filled in by metaclass
    __codecs_info__ = codecs.lookup('utf-8')
    __errors__ = 'strict'
    __nbytes__ = None
    __pad__ = b'\x00'
    __zero_termination__ = False

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        # pylint: disable=too-many-branches,too-many-locals

        original_offset = offset
        nbytes = cls.__nbytes__

        chunk, offset = getbytes(buffer, offset, nbytes, dump)

        if cls.__zero_termination__:

            decoder = cls.__codecs_info__.incrementaldecoder(cls.__errors__)

            if dump:
                dump.memory = b''

            zipped_char_bytes = []
            try:
                _decode_str_bytes(chunk, decoder, zipped_char_bytes, zero_termination=True)
            except UnicodeDecodeError:
                if dump:
                    _add_str_rows_to_dump(dump, zipped_char_bytes, buffer=chunk)
                raise

            nstr_membytes = len(b''.join(bytes(b) for c, b in zipped_char_bytes))
            termination = chunk[nstr_membytes:nstr_membytes + 1]

            if termination == b'\x00':
                leftover_bytes = chunk[nstr_membytes + 1:]
            else:
                leftover_bytes = chunk[nstr_membytes:]
                termination = b''

            if nbytes is None:
                offset = original_offset + nstr_membytes + len(termination)
                try:
                    seek = buffer.seek
                except AttributeError:
                    pass
                else:
                    seek(offset)
                leftover_bytes = b''

            if dump:
                _add_str_rows_to_dump(dump, zipped_char_bytes)
                if termination:
                    dump.add_record(access='--termination--', memory=bytes(termination))
                if leftover_bytes:
                    dump.add_extra_bytes('--pad--', bytes(leftover_bytes))

            if termination != b'\x00':
                raise InsufficientMemoryError('no zero termination present')

            self = ''.join(c for c, b in zipped_char_bytes)

        else:
            if dump:
                dump.memory = b''
                _add_str_bytes_to_dump(
                    dump, chunk, cls.__codecs_info__.incrementaldecoder(cls.__errors__))

            self = str(chunk, cls.__codecs_info__.name, cls.__errors__)

        return self, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        if dump:
            _add_str_value_to_dump(
                dump, value, cls.__codecs_info__.incrementalencoder(cls.__errors__))
            if cls.__zero_termination__:
                dump.add_record('--termination--', memory=b'\x00')

        chunk = value.encode(cls.__codecs_info__.name, cls.__errors__)

        if cls.__zero_termination__:
            chunk = chunk + b'\x00'

        nbytes = len(chunk)

        limit = cls.__nbytes__

        if limit is not None:

            if nbytes > limit:
                raise TypeError(
                    f'{cls.__name__} number of string bytes ({nbytes}) '
                    f'exceeds limit ({limit})')

            if nbytes < limit:
                pad = cls.__pad__ * (limit - nbytes)
                chunk += pad

                if dump and pad:
                    dump.add_extra_bytes('--pad--', pad)

        end = offset + nbytes
        buffer[offset:end] = chunk

        return end
