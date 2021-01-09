# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as IPV4 address."""

from .._plum import Plum, getbytes
from ._ipv4addresstype import IpV4AddressType


class IpV4Address(Plum, metaclass=IpV4AddressType, byteorder='little'):

    """IPV4 address, little endian format.

    :param address: IP address
    :type address: str or int or iterable

    """

    # filled in by metaclass
    __byteorder__ = 'little'
    __little_endian__ = True
    __nbytes__ = 4

    def __init__(self, address):
        try:
            # assume string
            octets = address.split('.')
        except (TypeError, AttributeError):
            # TypeError -> bytes like
            # AttributeError -> not a string or bytes like
            try:
                # assume iterable (e.g. bytearray, list, IpV4Address, etc)
                octets = list(address)
            except TypeError:
                try:
                    # assume integer
                    octets = address.to_bytes(4, self.__byteorder__, signed=False)
                except AttributeError:
                    raise TypeError(f'invalid IPV4 address: {address!r}')
            else:
                if not self.__little_endian__:
                    octets.reverse()
        else:
            if self.__little_endian__:
                octets.reverse()

        if len(octets) != 4:
            raise ValueError(f'invalid IPV4 address: {address!r}')

        self.__octets__ = bytes(int(octet) for octet in octets)

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        octets, offset = getbytes(buffer, offset, 4, dump)

        address = object.__new__(cls)
        address.__octets__ = bytes(octets)

        if dump:
            dump.value = str(address)

        return address, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        end = offset + 4

        try:
            if not isinstance(value, cls):
                value = cls(value)

            buffer[offset:end] = value.__octets__

        finally:
            if dump:
                dump.value = str(value)
                dump.memory = buffer[offset:end]

        return end

    def __str__(self):
        if self.__little_endian__:
            address = '.'.join(str(octet) for octet in reversed(self.__octets__))
        else:
            address = '.'.join(str(octet) for octet in self.__octets__)
        return address

    def __repr__(self):
        return f'{type(self).__name__}({str(self)!r})'

    @classmethod
    def _convert_to_int(cls, other):
        if not isinstance(other, int):
            other = int(cls(other))
        return other

    def __lt__(self, other):
        return int(self).__lt__(self._convert_to_int(other))

    def __le__(self, other):
        return int(self).__le__(self._convert_to_int(other))

    def __eq__(self, other):
        return int(self).__eq__(self._convert_to_int(other))

    def __ne__(self, other):
        return int(self).__ne__(self._convert_to_int(other))

    def __gt__(self, other):
        return int(self).__gt__(self._convert_to_int(other))

    def __ge__(self, other):
        return int(self).__ge__(self._convert_to_int(other))

    def __hash__(self):
        return int(self).__hash__()

    def __bool__(self):
        return bool(int(self))

    def __and__(self, other):
        return type(self)(int(self).__and__(self._convert_to_int(other)))

    def __xor__(self, other):
        return type(self)(int(self).__xor__(self._convert_to_int(other)))

    def __or__(self, other):
        return type(self)(int(self).__or__(self._convert_to_int(other)))

    def __rand__(self, other):
        return type(self)(int(self).__rand__(self._convert_to_int(other)))

    def __rxor__(self, other):
        return type(self)(int(self).__rxor__(self._convert_to_int(other)))

    def __ror__(self, other):
        return type(self)(int(self).__ror__(self._convert_to_int(other)))

    def __iand__(self, other):
        address = type(self)(int(self).__and__(self._convert_to_int(other)))
        self.__octets__ = address.__octets__
        return self

    def __ixor__(self, other):
        address = type(self)(int(self).__xor__(self._convert_to_int(other)))
        self.__octets__ = address.__octets__
        return self

    def __ior__(self, other):
        address = type(self)(int(self).__or__(self._convert_to_int(other)))
        self.__octets__ = address.__octets__
        return self

    def __int__(self):
        return int.from_bytes(self.__octets__, self.__byteorder__, signed=False)

    def __float__(self):
        return float(int(self))

    def __iter__(self):
        if self.__little_endian__:
            yield from self.__octets__
        else:
            yield from reversed(self.__octets__)

    def __getitem__(self, index):
        return self.__octets__[index]

    def __setitem__(self, key, value):
        buffer = bytearray(
            self.__octets__ if self.__little_endian__ else reversed(self.__octets__))

        buffer[key] = value

        if len(buffer) != 4:
            raise ValueError('invalid number of address octets')

        self.__octets__ = bytes(buffer if self.__little_endian__ else reversed(buffer))

    def __len__(self):
        return 4
