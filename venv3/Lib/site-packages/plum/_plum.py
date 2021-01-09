# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Packable/Unpacked bytes base class."""

# pylint: disable=too-many-lines

import functools

from ._dump import Dump

from ._exceptions import (
    ExcessMemoryError,
    ImplementationError,
    InsufficientMemoryError,
    PackError,
    SizeError,
    UnpackError,
)
from ._plumtype import PlumType


class SizeProperty:

    """Size in bytes of packed plum instance."""

    def __get__(self, obj, objtype):
        nbytes = objtype.__nbytes__

        if nbytes is None:
            if obj is None:
                raise SizeError(f'{objtype.__name__!r} instance sizes vary')

            nbytes = len(pack(type(obj), obj))

        return nbytes


class PackMethod:

    """Pack class/instance method facilitator."""

    def __init__(self, method):
        self.__func__ = method

    def __get__(self, obj, objtype):
        if obj is None:
            method = functools.partial(self.__func__, objtype)
        else:
            method = functools.partial(self.__func__, objtype, item=obj)

        return method


class Plum:

    """Packable/Unpacked bytes base class."""

    __nbytes__ = None

    nbytes = SizeProperty()

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):  # pragma: no cover
        raise NotImplementedError(f'{cls.__name__!r} does not support plum.unpack()')

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):  # pragma: no cover
        raise NotImplementedError(f'{cls.__name__!r} does not support plum.pack()')

    @classmethod
    def __view__(cls, buffer, offset=0):
        """Create plum view of bytes buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. ``bytes``, ``bytearray``, ``memoryview``)
        :param int offset: byte offset

        """
        raise TypeError(f'{cls.__name__!r} does not support view()')

    @property
    def dump(self):
        """Packed bytes summary.

        :returns: summary table of view detailing bytes and layout
        :rtype: str

        """
        dump = Dump()
        # arguments: fmt, buffer, offset(0), args, kwargs, parent(None), dump
        _pack_with_format(type(self), bytearray(), 0, (self,), {}, None, dump)
        return dump

    @PackMethod
    def pack(cls, item=None):  # pylint: disable=no-self-argument
        r"""Pack item as bytes.

        :param object item: packable item
        :returns: bytes buffer
        :rtype: bytearray

        For example:

            >>> from plum.int.little import UInt16
            >>> # use as class method (pass a value)
            >>> UInt16.pack(2)
            bytearray(b'\x02\x00')
            >>> # use as instance method (pass value to constructor))
            >>> UInt16(2).pack()
            bytearray(b'\x02\x00')

        """
        return pack(cls, item)

    @PackMethod
    def pack_and_dump(cls, item=None):  # pylint: disable=no-self-argument
        """Pack item as bytes and produce bytes summary.

        :param object item: packable item
        :returns: bytes buffer, packed bytes summary
        :rtype: bytearray, Dump

        For example:

            >>> from plum.int.little import UInt16
            >>> # use as class method (pass a value as last argument)
            >>> membytes, dump = UInt16.pack_and_dump(2)
            >>> membytes
            bytearray(b'\x02\x00')
            >>> print(dump)
            +--------+-------+-------+--------+
            | Offset | Value | Bytes | Type   |
            +--------+-------+-------+--------+
            | 0      | 2     | 02 00 | UInt16 |
            +--------+-------+-------+--------+
            >>> # use as instance method (pass value to constructor))
            >>> membytes, dump = UInt16(2).pack_and_dump()
            >>> membytes
            bytearray(b'\x02\x00')
            >>> print(dump)
            +--------+-------+-------+--------+
            | Offset | Value | Bytes | Type   |
            +--------+-------+-------+--------+
            | 0      | 2     | 02 00 | UInt16 |
            +--------+-------+-------+--------+

        """
        return pack_and_dump(cls, item)

    @PackMethod
    def pack_into(cls, buffer, offset, item=None):  # pylint: disable=no-self-argument
        r"""Pack item as bytes into a buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytearray, memoryview)
        :param int offset: start location within bytes buffer
        :param object item: packable item

        For example:

            >>> from plum.int.little import UInt8
            >>>
            >>> buffer = bytearray(4)
            >>> # use as class method (pass a value as last argument)
            >>> UInt8.pack_into(buffer, 1, 0x11)
            >>> # use as instance method (pass value to constructor))
            >>> UInt8(0x12).pack_into(buffer, 2)
            >>> buffer
            bytearray(b'\x00\x11\x12\x00')

        """
        # fmt -> cls
        pack_into(cls, buffer, offset, item)

    @PackMethod
    def pack_into_and_dump(cls, buffer, offset, item=None):
        r"""Pack item as bytes into a buffer and produce bytes summary.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytearray, memoryview)
        :param int offset: start location within bytes buffer
        :param object item: packable item
        :returns: packed bytes summary
        :rtype: Dump

        For example:

            >>> from plum.int.little import UInt8
            >>>
            >>> buffer = bytearray(4)
            >>> # use as class method (pass a value as last argument)
            >>> dump = UInt8.pack_into_and_dump(buffer, 1, 0x11)
            >>> print(dump)
            +--------+-------+-------+-------+
            | Offset | Value | Bytes | Type  |
            +--------+-------+-------+-------+
            | 1      | 17    | 11    | UInt8 |
            +--------+-------+-------+-------+
            >>> # use as instance method (pass value to constructor))
            >>> dump = UInt8(0x12).pack_into_and_dump(buffer, 2)
            >>> print(dump)
            +--------+-------+-------+-------+
            | Offset | Value | Bytes | Type  |
            +--------+-------+-------+-------+
            | 2      | 18    | 12    | UInt8 |
            +--------+-------+-------+-------+
            >>> buffer
            bytearray(b'\x00\x11\x12\x00')

        """
        # pylint: disable=no-self-argument
        # fmt -> cls
        return pack_into_and_dump(cls, buffer, offset, item)

    @classmethod
    def unpack(cls, buffer):  # pragma: no cover
        r"""Unpack item from bytes.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
        :returns: unpacked value
        :rtype: object (cls or type associated with cls)
        :raises: ``UnpackError`` if insufficient bytes, excess bytes, or value error

        For example:
            >>> from plum.int.little import UInt16
            >>> UInt16.unpack(b'\x01\x02')
            513

        """
        return unpack(cls, buffer)

    @classmethod
    def unpack_and_dump(cls, buffer):
        r"""Unpack item from bytes and produce packed bytes summary.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
        :returns: tuple of (unpacked value, bytes summary)
        :rtype: object (cls or type associated with cls), Dump
        :raises: ``UnpackError`` if insufficient bytes, excess bytes, or value error

        For example:
            >>> from plum.int.little import UInt16
            >>> value, dump = UInt16.unpack_and_dump(b'\x01\x02')
            >>> value
            513
            >>> print(dump)
            +--------+-------+-------+--------+
            | Offset | Value | Bytes | Type   |
            +--------+-------+-------+--------+
            | 0      | 513   | 01 02 | UInt16 |
            +--------+-------+-------+--------+

        """
        return unpack_and_dump(cls, buffer)

    @classmethod
    def unpack_from(cls, buffer, offset=None):
        r"""Unpack item from within a bytes buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
        :param int offset: starting byte offset (``None`` indicates current file position)
        :returns: unpacked value
        :rtype: object (cls or type associated with cls)
        :raises: ``UnpackError`` if insufficient bytes or value error

        For example:
            >>> from plum.int.little import UInt8
            >>> buffer = b'\x99\x01\x99'
            >>> UInt8.unpack_from(buffer, offset=1)
            1

        """
        return unpack_from(cls, buffer, offset)

    @classmethod
    def unpack_from_and_dump(cls, buffer, offset=None):
        """Unpack item from within a bytes buffer and produce packed bytes summary.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
        :param int offset: starting byte offset (``None`` indicates current file position)
        :returns: tuple of (unpacked items, bytes summary)
        :rtype: Plum (or tuple of Plum, or dict of Plum, dependent on ``fmt``), Dump
        :raises: ``UnpackError`` if insufficient bytes, or value error

        For example:
            >>> from plum.int.little import UInt8
            >>> buffer = b'\x99\x01\x99'
            >>> value, dump = UInt8.unpack_from_and_dump(buffer, offset=1)
            >>> value
            1
            >>> print(dump)
            +--------+-------+-------+-------+
            | Offset | Value | Bytes | Type  |
            +--------+-------+-------+-------+
            | 1      | 1     | 01    | UInt8 |
            +--------+-------+-------+-------+

        """
        return unpack_from_and_dump(cls, buffer, offset)

    @classmethod
    def view(cls, buffer, offset=0):
        """Create plum view of bytes buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
        :param int offset: byte offset

        For example:
            >>> from plum.int.little import UInt16
            >>> buffer = b'\x01\x02\x03\x04'
            >>> value = UInt16.view(buffer, offset=1)
            >>> value
            <view at 0x1: UInt16(770)>
            >>> value == 770
            True

        """
        return cls.__view__(buffer, offset)

    def __eq__(self, other):  # pragma: no cover
        return self.pack() == type(self).pack(other)

    def __ne__(self, other):  # pragma: no cover
        return self.pack() != type(self).pack(other)


def getbytes(buffer, offset, nbytes=None, dump=None):
    """Get bytes from buffer.

    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
    :param int offset: offset into bytes buffer
    :param int nbytes: bytes to consume (``None`` returns remainder)
    :param Dump dump: bytes summary dump (``None`` skips dump annotation)
    :returns: tuple of (requested bytes, offset)
    :rtype: bytes-like, int, int or None

    """
    if nbytes is None:
        try:
            chunk = buffer[offset:]
        except TypeError:
            chunk = buffer.read()

        offset += len(chunk)

        if dump:
            dump.memory = chunk

    else:
        start = offset
        offset += nbytes
        try:
            chunk = buffer[start: offset]
        except TypeError:
            chunk = buffer.read(nbytes)

        if len(chunk) < nbytes:
            if dump:
                dump.value = '<insufficient bytes>'
                if len(chunk) > 16:
                    dump.add_extra_bytes('', chunk)
                else:
                    dump.memory = chunk

            cls_name = f'{dump.cls.__name__} ' if dump and dump.cls else ''

            unpack_shortage = (
                f'{nbytes - len(chunk)} too few bytes to unpack {cls_name}'
                f'({nbytes} needed, only {len(chunk)} available)')

            raise InsufficientMemoryError(unpack_shortage)

        if dump:
            dump.memory = chunk

    return chunk, offset


def _pack_value_with_format(fmt, buffer, offset, parent, value, dump):
    # pylint: disable=too-many-statements,too-many-branches,
    # pylint: disable=too-many-locals,too-many-nested-blocks

    if isinstance(fmt, PlumType):
        if dump:
            dump.cls = fmt
        offset = fmt.__pack__(buffer, offset, parent, value, dump)

    elif isinstance(fmt, dict):
        if isinstance(value, dict):
            missing = []
            for key, subfmt in fmt.items():
                try:
                    item = value[key]
                except KeyError:
                    missing.append(key)
                    if dump:
                        record = dump.add_record(access=f'[{key!r}]', value='(missing)')
                        if isinstance(subfmt, PlumType):
                            record.cls = subfmt
                else:
                    offset = _pack_value_with_format(
                        subfmt, buffer, offset, parent, item,
                        dump.add_record(access=f'[{key!r}]') if dump else dump)

            if missing:
                value_s = "value" if len(missing) == 1 else "values"
                names = ", ".join(repr(name) for name in missing)
                raise TypeError(f'missing {value_s}: {names}')

            extra_keys = set(value) - set(fmt)

            if extra_keys:
                if dump:
                    separate = True
                    for name in extra_keys:
                        dump.add_record(
                            access=f'[{name!r}]', value=value[name],
                            cls='(unexpected)', separate=separate)
                        separate = False

                value_s = "value" if len(extra_keys) == 1 else "values"
                names = ", ".join(repr(name) for name in extra_keys)
                raise TypeError(f'unexpected {value_s}: {names}')
        else:
            if dump:
                dump.value = value
            raise TypeError(f'invalid value, expected dict, got {value!r}')

    elif isinstance(fmt, (tuple, list)):
        if isinstance(value, (tuple, list)):
            for i, (subfmt, item) in enumerate(zip(fmt, value)):
                offset = _pack_value_with_format(
                    subfmt, buffer, offset, parent, item,
                    dump.add_record(access=f'[{i}]') if dump else dump)

            if len(value) != len(fmt):
                if dump:
                    if len(value) < len(fmt):
                        for i in range(len(value), len(fmt)):
                            dump.add_record(
                                cls=fmt[i], value='(missing)', access=f'[{i}]')
                    else:
                        separate = True
                        for i in range(len(fmt), len(value)):
                            dump.add_record(
                                cls='(unexpected)', value=value[i],
                                access=f'[{i}]', separate=separate)
                            separate = False

                value_s = "value" if len(value) == 1 else "values"
                raise TypeError(f'{len(value)} {value_s} given, expected {len(fmt)}')
        else:
            if dump:
                dump.cls = 'tuple or list'
                dump.value = value
            raise TypeError(f'invalid value, expected tuple or list, got {value!r}')

    else:
        if dump:
            record = dump.add_record() if isinstance(dump, Dump) else dump
            try:
                # assume class and use name
                record.cls = fmt.__name__ + ' (invalid)'
            except AttributeError:
                # must be an instance
                record.cls = str(fmt) + ' (invalid)'

            record.value = value

        raise TypeError(
            f'bad format, expected tuple, list, dict, or PlumType, got {fmt!r}')

    return offset


def _pack_with_format(fmt, buffer, offset, args, kwargs, parent, dump):
    # pylint: disable=too-many-branches,too-many-arguments,too-many-locals
    # pylint: disable=too-many-nested-blocks
    try:
        if isinstance(fmt, PlumType):
            if args:
                subdmp = None if dump is None else dump.add_record(cls=fmt)
                offset = fmt.__pack__(buffer, offset, parent, args[0], subdmp)

            if len(args) != 1:
                if dump:
                    if args:
                        for value in args[1:]:
                            dump.add_record(cls='(unexpected)', value=value)
                    else:
                        dump.add_record(cls=fmt, value='(missing)')
                value_s = 'value' if len(args) == 1 else 'values'
                raise TypeError(f'{len(args)} {value_s} given, expected 1')

            if kwargs:
                if dump:
                    for key, value in kwargs.items():
                        dump.add_record(access=key, cls='(unexpected)', value=value)
                value_s = 'value' if len(kwargs) == 1 else 'values'
                names = ", ".join(repr(k) for k in kwargs)
                raise TypeError(
                    f'unexpected keyword argument {value_s}: {names}')

        elif isinstance(fmt, (tuple, list)):
            offset = _pack_value_with_format(fmt, buffer, offset, parent, args, dump)

            if kwargs:
                if dump:
                    separate = True
                    for key, value in kwargs.items():
                        dump.add_record(
                            access=f'[{key!r}]', value=value,
                            cls='(unexpected)', separate=separate)
                        separate = False

                value_s = 'value' if len(kwargs) == 1 else 'values'
                names = ", ".join(repr(k) for k in kwargs)
                raise TypeError(f'unexpected keyword argument {value_s}: {names}')

        elif isinstance(fmt, dict):
            offset = _pack_value_with_format(fmt, buffer, offset, parent, kwargs, dump)

            if args:
                if dump:
                    separate = True
                    for arg in args:
                        dump.add_record(value=arg, cls='(unexpected)', separate=separate)
                        separate = False
                value_s = "value" if len(args) == 1 else "values"
                raise TypeError(f'got {len(args)} unexpected {value_s}')

        else:
            # generate exception
            offset = _pack_value_with_format(
                fmt, buffer, offset, parent, args[0] if args else kwargs, dump)

    except Exception as exc:
        if isinstance(dump, Dump):
            unexpected_exception = (
                f"\n\n{dump}\n\n"
                f"{type(exc).__name__} occurred during pack operation:"
                f"\n\n{exc}")

            raise PackError(unexpected_exception)

        raise

    return offset


def pack(fmt, *args, **kwargs):
    r"""Pack values as bytes following a format.

    :param fmt: byte format of values
    :type fmt: Plum, tuple/list of Plum, or dict of Plum
    :param tuple args: packable values
    :param kwargs: packable values
    :returns: bytes buffer
    :rtype: bytearray

    For example:

        >>> from plum import pack
        >>> from plum.int.little import UInt8, UInt16
        >>> pack(UInt8, 1)
        bytearray(b'\x01')
        >>> pack((UInt8, UInt8), 1, 2)
        bytearray(b'\x01\x02')
        >>> pack({'a': UInt8, 'b': UInt8}, a=1, b=2)
        bytearray(b'\x01\x02')


    """
    buffer = bytearray()

    try:
        # attempt w/o dump for performance
        # parent, dump -> None, None
        _pack_with_format(fmt, buffer, 0, args, kwargs, None, None)
    except Exception:
        # do it over to include dump in exception message
        # parent -> None
        _pack_with_format(fmt, buffer, 0, args, kwargs, None, Dump())
        raise ImplementationError()  # pragma: no cover

    return buffer


def pack_and_dump(fmt, *args, **kwargs):
    """Pack values as bytes and produce bytes summary following a format.

    :param fmt: byte format of values
    :type fmt: Plum, tuple/list of Plum, or dict of Plum
    :param tuple args: packable values
    :param kwargs: packable values
    :returns: bytes buffer, packed bytes summary
    :rtype: bytearray, Dump

    For example:

        >>> from plum import pack_and_dump
        >>> from plum.int.little import UInt8, UInt16
        >>>
        >>> buffer, dump = pack_and_dump(UInt8, 1)
        >>> buffer
        bytearray(b'\x01')
        >>> print(dump)
        +--------+-------+-------+-------+
        | Offset | Value | Bytes | Type  |
        +--------+-------+-------+-------+
        | 0      | 1     | 01    | UInt8 |
        +--------+-------+-------+-------+
        >>>
        >>> buffer, dump = pack_and_dump((UInt8, UInt8), 1, 2)
        >>> buffer
        bytearray(b'\x01\x02')
        >>> print(dump)
        +--------+--------+-------+-------+-------+
        | Offset | Access | Value | Bytes | Type  |
        +--------+--------+-------+-------+-------+
        | 0      | [0]    | 1     | 01    | UInt8 |
        | 1      | [1]    | 2     | 02    | UInt8 |
        +--------+--------+-------+-------+-------+
        >>>
        >>> buffer, dump = pack_and_dump({'a': UInt8, 'b': UInt8}, a=1, b=2)
        >>> buffer
        bytearray(b'\x01\x02')
        >>> print(dump)
        +--------+--------+-------+-------+-------+
        | Offset | Access | Value | Bytes | Type  |
        +--------+--------+-------+-------+-------+
        | 0      | ['a']  | 1     | 01    | UInt8 |
        | 1      | ['b']  | 2     | 02    | UInt8 |
        +--------+--------+-------+-------+-------+

    """
    buffer = bytearray()
    dump = Dump()
    # parent -> None
    _pack_with_format(fmt, buffer, 0, args, kwargs, None, dump)
    return buffer, dump


def pack_into(fmt, buffer, offset, *args, **kwargs):
    r"""Pack values as bytes into a buffer following a format.

    :param fmt: byte format of values
    :type fmt: Plum, tuple/list of Plum, or dict of Plum
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytearray, memoryview)
    :param int offset: start location within bytes buffer
    :param tuple args: packable values
    :param kwargs: packable values

    For example:

        >>> from plum import pack_into
        >>> from plum.int.little import UInt8, UInt16
        >>>
        >>> fmt = (UInt8, UInt16)
        >>> buffer = bytearray(5)
        >>> offset = 1
        >>>
        >>> pack_into(fmt, buffer, offset, 0x11, 0x0302)
        >>> buffer
        bytearray(b'\x00\x11\x02\x03\x00')

    """
    offset = _adjust_and_validate_offset(buffer, offset)

    try:
        # attempt w/o dump for performance
        temp_buffer = pack(fmt, *args, **kwargs)
    except Exception:
        # do it over to include dump in exception message
        # parent -> None
        _pack_with_format(fmt, bytearray(), 0, args, kwargs, None, Dump(offset=offset))
        raise ImplementationError()  # pragma: no cover

    try:
        buffer[offset:offset + len(temp_buffer)] = temp_buffer
    except Exception as exc:
        unexpected_exception = (
            f"{type(exc).__name__} occurred during pack operation:"
            f"\n\n{exc}")

        raise PackError(unexpected_exception)


def pack_into_and_dump(fmt, buffer, offset, *args, **kwargs):
    r"""Pack values as bytes into a buffer following a format and produce bytes summary.

    :param fmt: byte format of values
    :type fmt: Plum, tuple/list of Plum, or dict of Plum
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytearray, memoryview)
    :param int offset: start location within bytes buffer
    :param tuple args: packable values
    :param kwargs: packable values
    :returns: packed bytes summary
    :rtype: Dump

    For example:

        >>> from plum import pack_into_and_dump
        >>> from plum.int.little import UInt8, UInt16
        >>>
        >>> fmt = (UInt8, UInt16)
        >>> buffer = bytearray(5)
        >>> offset = 1
        >>>
        >>> dump = pack_into_and_dump(fmt, buffer, offset, 0x11, 0x0302)
        >>> print(dump)
        +--------+--------+-------+-------+--------+
        | Offset | Access | Value | Bytes | Type   |
        +--------+--------+-------+-------+--------+
        | 1      | [0]    | 17    | 11    | UInt8  |
        | 2      | [1]    | 770   | 02 03 | UInt16 |
        +--------+--------+-------+-------+--------+
        >>> buffer
        bytearray(b'\x00\x11\x02\x03\x00')

    """
    offset = _adjust_and_validate_offset(buffer, offset)

    dump = Dump(offset=offset)

    temp_buffer = bytearray()
    # parent -> None
    _pack_with_format(fmt, temp_buffer, 0, args, kwargs, None, dump)

    try:
        buffer[offset:offset + len(temp_buffer)] = temp_buffer
    except Exception as exc:
        unexpected_exception = (
            f"{type(exc).__name__} occurred during pack operation:"
            f"\n\n{exc}")

        raise PackError(unexpected_exception)

    return dump


def _adjust_and_validate_offset(buffer, offset):
    buffer_len = len(buffer)

    if offset < 0:
        adjusted_offset = buffer_len + offset
    else:
        adjusted_offset = offset

    if (adjusted_offset < 0) or (adjusted_offset > buffer_len):
        raise PackError(
            f'offset {offset} out of range for {buffer_len}-byte buffer')

    return adjusted_offset


def _unpack(fmt, buffer, offset, prohibit_excess, dump):
    # pylint: disable=too-many-branches,too-many-locals
    # pylint: disable=too-many-statements,too-many-nested-blocks
    original_dump = dump
    original_offset = offset

    try:
        if isinstance(fmt, PlumType):
            if dump:
                if isinstance(dump, Dump):
                    dump = dump.add_record(cls=fmt)
                else:
                    dump.cls = fmt
            # None -> no parent
            items, offset = fmt.__unpack__(buffer, offset, None, dump)

        elif isinstance(fmt, tuple):
            items = []
            for i, cls in enumerate(fmt):
                item, offset = _unpack(
                    cls, buffer, offset,
                    False,  # prohibit_excess
                    dump.add_record(access=f'[{i}]') if dump else dump)
                items.append(item)
            items = tuple(items)

        elif isinstance(fmt, list):
            items = []
            for i, cls in enumerate(fmt):
                item, offset = _unpack(
                    cls, buffer, offset,
                    False,  # prohibit_excess
                    dump.add_record(access=f'[{i}]') if dump else dump)
                items.append(item)

        elif isinstance(fmt, dict):
            items = {}
            for name, cls in fmt.items():
                item, offset = _unpack(
                    cls, buffer, offset,
                    False,  # prohibit excess
                    dump.add_record(access=f'[{name!r}]') if dump else dump)
                items[name] = item

        else:
            if dump:
                if isinstance(dump, Dump):
                    dump.add_record(cls=fmt)
                else:
                    dump.cls = fmt
            raise TypeError('fmt must specify a Plum type (or a dict, tuple, or list of them)')

        if prohibit_excess:
            try:
                extra_bytes = buffer.read()
            except AttributeError:
                extra_bytes = buffer[offset:]

            if extra_bytes:
                if dump:
                    for i in range(0, len(extra_bytes), 16):
                        record = dump.add_record(memory=extra_bytes[i:i + 16])
                        if not i:
                            record.separate = True
                            record.value = '<excess bytes>'

                raise ExcessMemoryError(
                    f'{len(extra_bytes)} unconsumed bytes', extra_bytes)

    except Exception as exc:
        try:
            buffer.seek(original_offset)
        except Exception:  # pylint: disable=broad-except
            pass  # must be bytes or bytearray

        if isinstance(original_dump, Dump):
            unexpected_exception = (
                f"\n\n{original_dump}\n\n"
                f"{type(exc).__name__} occurred during unpack operation:"
                f"\n\n{exc}")

            raise UnpackError(unexpected_exception)

        raise

    return items, offset


def unpack(fmt, buffer):
    r"""Unpack item(s) from bytes.

    :param fmt: plum type, tuple of types, or dict of types
    :type fmt: Plum, tuple of Plum, or dict
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
    :returns: unpacked items
    :rtype: Plum, tuple of Plum, or dict of Plum (dependent on ``fmt``)
    :raises: ``UnpackError`` if insufficient bytes, excess bytes, or value error

    For example:
        >>> from plum import unpack
        >>> from plum.int.little import UInt8, UInt16
        >>> unpack(UInt16, b'\x01\x02')
        513
        >>> unpack((UInt8, UInt16), b'\x00\x01\x02')
        (0, 513)
        >>> unpack({'a': UInt8, 'b': UInt16}, b'\x00\x01\x02')
        {'a': 0, 'b': 513}

    """
    try:
        try:
            buffer.seek(0)
        except AttributeError:
            pass

        # _unpack(fmt, buffer, offset, prohibit_excess, dump)
        items, _offset = _unpack(fmt, buffer, 0, True, None)
    except Exception:
        # do it over to include dump in exception message
        unpack_and_dump(fmt, buffer)
        raise ImplementationError()  # pragma: no cover

    return items


def unpack_and_dump(fmt, buffer):
    r"""Unpack item(s) from bytes and produce packed bytes summary.

    :param fmt: plum type, tuple of types, or dict of types
    :type fmt: Plum, tuple of Plum, or dict
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
    :returns: tuple of (unpacked items, bytes summary)
    :rtype: Plum (or tuple of Plum, or dict of Plum, dependent on ``fmt``), Dump
    :raises: ``UnpackError`` if insufficient bytes, excess bytes, or value error

    For example:
        >>> from plum import unpack_and_dump
        >>> from plum.int.little import UInt8, UInt16
        >>>
        >>> value, dump = unpack_and_dump((UInt8, UInt16), b'\x00\x01\x02')
        >>> value
        (0, 513)
        >>> print(dump)
        +--------+--------+-------+-------+--------+
        | Offset | Access | Value | Bytes | Type   |
        +--------+--------+-------+-------+--------+
        | 0      | [0]    | 0     | 00    | UInt8  |
        | 1      | [1]    | 513   | 01 02 | UInt16 |
        +--------+--------+-------+-------+--------+

    """
    dump = Dump()

    try:
        buffer.seek(0)
    except AttributeError:
        pass
    except Exception as exc:  # pylint: disable=broad-except
        # buffer operation failed, mimic _unpack( ) exception handling
        unexpected_exception = (
            f"\n\n{dump}\n\n"
            f"{type(exc).__name__} occurred during unpack operation:"
            f"\n\n{exc}")
        raise UnpackError(unexpected_exception)

    items, _offset = _unpack(fmt, buffer, 0, True, dump)

    return items, dump


def unpack_from(fmt, buffer, offset=None):
    r"""Unpack item from within a bytes buffer.

    :param fmt: plum type, tuple of types, or dict of types
    :type fmt: Plum, tuple of Plum, or dict
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
    :param int offset: starting byte offset (``None`` indicates current file position)
    :returns: unpacked items
    :rtype: Plum, tuple of Plum, or dict of Plum (dependent on ``fmt``)
    :raises: ``UnpackError`` if insufficient bytes or value error

    For example:
        >>> from plum import unpack_from
        >>> from plum.int.little import UInt8
        >>>
        >>> buffer = b'\x99\x01\x99'
        >>> offset = 1
        >>>
        >>> unpack_from(UInt8, buffer, offset)
        1

    """
    try:
        if offset is None:
            try:
                offset = buffer.tell()
            except AttributeError:
                offset = 0
        else:
            try:
                buffer.seek(offset)
            except AttributeError:
                pass

        # _unpack(fmt, buffer, offset, prohibit_excess, dump)
        items, _offset = _unpack(fmt, buffer, offset, False, None)
    except Exception:
        # do it over to include dump in exception message
        unpack_from_and_dump(fmt, buffer, offset)
        raise ImplementationError()  # pragma: no cover

    return items


def unpack_from_and_dump(fmt, buffer, offset=None):
    r"""Unpack item from within a bytes buffer and produce packed bytes summary.

    :param fmt: plum type, tuple of types, or dict of types
    :type fmt: Plum, tuple of Plum, or dict
    :param buffer: bytes buffer
    :type buffer: bytes-like (e.g. bytes, bytearray, memoryview) or binary file
    :param int offset: starting byte offset (``None`` indicates current file position)
    :returns: tuple of (unpacked items, bytes summary)
    :rtype: Plum (or tuple of Plum, or dict of Plum, dependent on ``fmt``), Dump
    :raises: ``UnpackError`` if insufficient bytes or value error

    For example:
        >>> from plum import unpack_from_and_dump
        >>> from plum.int.little import UInt8
        >>>
        >>> buffer = b'\x99\x01\x99'
        >>> offset = 1
        >>>
        >>> value, dump = unpack_from_and_dump(UInt8, buffer, offset)
        >>> value
        1
        >>> print(dump)
        +--------+-------+-------+-------+
        | Offset | Value | Bytes | Type  |
        +--------+-------+-------+-------+
        | 1      | 1     | 01    | UInt8 |
        +--------+-------+-------+-------+

    """
    dump = Dump()

    try:
        if offset is None:
            try:
                offset = buffer.tell()
            except AttributeError:
                offset = 0
        else:
            try:
                buffer.seek(offset)
            except AttributeError:
                pass

        dump.offset = int(offset)

    except Exception as exc:
        # buffer operation failed, mimic _unpack( ) exception handling
        unexpected_exception = (
            f"\n\n{dump}\n\n"
            f"{type(exc).__name__} occurred during unpack operation:"
            f"\n\n{exc}")
        raise UnpackError(unexpected_exception)

    # _unpack(fmt, buffer, offset, prohibit_excess, dump)
    items, _offset = _unpack(fmt, buffer, offset, False, dump)

    return items, dump


# for easy injection of boost versions of utilities into this namespace
plum_namespace = globals()

# make references to original docstrings for boost docstring tests
pack_doc = pack.__doc__
packmethod_doc = Plum.pack.func.__doc__  # pylint: disable=no-member
unpack_doc = unpack.__doc__
unpack_from_doc = unpack_from.__doc__
unpackmethod_doc = Plum.unpack.__func__.__doc__  # pylint: disable=no-member

# slightly faster to not have middle-man
Plum.unpack = classmethod(unpack)
