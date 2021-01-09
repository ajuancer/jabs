# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""BitFields type."""

from ..._plum import Plum, getbytes
from ._bitfieldstype import BitFieldsType


class BitFields(Plum, metaclass=BitFieldsType, nbytes=4, byteorder='little', default=0, ignore=0):

    """Interpret bytes as an unsigned integer with bit fields."""

    # filled in by metaclass
    __byteorder__ = 'little'
    __compare_mask__ = 0xffffffff
    __fields__ = dict()
    __default__ = 0
    __fields_with_defaults__ = set()
    __ignore__ = 0
    __max__ = 0xffffffff
    __nbytes__ = 4

    def __init__(self, *args, **kwargs):
        cls = type(self)

        try:
            value = int(args[0])
        except (IndexError, TypeError):
            self.__value__ = cls.__default__
        else:
            args = args[1:]

            if args:
                raise TypeError(
                    f'{cls.__name__} expected at most 1 arguments, got {len(args) + 1}')

            if kwargs:
                raise TypeError('cannot specify both integer value and keyword arguments')

            if (value < 0) or (value > cls.__max__):
                raise ValueError(
                    f'{cls.__name__} requires 0 <= number <= {cls.__max__}')

            self.__value__ = value

        field_values = dict(*args, **kwargs)

        if field_values:
            accessors = cls.__fields__

            extras = set(field_values) - set(accessors)

            if extras:
                plural = 's' if len(extras) > 1 else ''
                message = (
                    f'{cls.__name__}() '
                    f'got {len(extras)} unexpected bit field{plural}: ')
                message += ', '.join(repr(e) for e in sorted(extras))
                raise TypeError(message)

            missing = set(accessors) - set(field_values) - cls.__fields_with_defaults__

            if missing:
                plural = 's' if len(missing) > 1 else ''
                message = (
                    f'{cls.__name__}() '
                    f'missing {len(missing)} required bit field{plural}: ')
                message += ', '.join(repr(m) for m in sorted(missing))
                raise TypeError(message)

            for name, value in field_values.items():
                accessors[name].__set__(self, value)

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        chunk, offset = getbytes(buffer, offset, cls.__nbytes__, dump)

        int_value = int.from_bytes(chunk, cls.__byteorder__, signed=False)

        bitfields = cls.__new__(cls, int_value)
        cls.__init__(bitfields, int_value)

        if dump:
            dump.value = bitfields.__value__
            cls.__add_bitfields_to_dump__(bitfields, dump)

        return bitfields, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        try:
            int_value = int(value)
        except TypeError:
            # support dictionary values
            value = cls(value)
            int_value = value.__value__

        nbytes = cls.__nbytes__

        chunk = int_value.to_bytes(nbytes, cls.__byteorder__, signed=False)

        end = offset + nbytes
        buffer[offset:end] = chunk

        if dump:
            dump.value = str(int_value)
            dump.memory = chunk
            cls.__add_bitfields_to_dump__(value, dump)

        return end

    @classmethod
    def __add_bitfields_to_dump__(cls, bitfields, dump, bitoffset=0):
        if not isinstance(bitfields, cls):
            bitfields = cls(bitfields)

        for name, accessor in cls.__fields__.items():
            bitfield_cls = accessor.cls

            if issubclass(bitfield_cls, BitFields):
                row = dump.add_record(access='.' + name, cls=bitfield_cls)
                bitfield_cls.__add_bitfields_to_dump__(
                    getattr(cls, name).__get__(bitfields, cls), row, bitoffset + accessor.pos)

            else:
                dump.add_record(
                    access='.' + name,
                    bits=(bitoffset + accessor.pos, accessor.size),
                    value=str(getattr(cls, name).__get__(bitfields, cls)),
                    cls=bitfield_cls)

    def __repr__(self):
        # str( ) around getattr formats enumerations correctly (otherwise shows
        # as int)
        args = ', '.join(f'{n}={str(getattr(self, n))}' for n in self.__fields__)
        return f'{type(self).__name__}({args})'

    @classmethod
    def _normalize_for_compare(cls, value, other):
        if isinstance(other, cls):
            other = other.__value__ & cls.__compare_mask__
            value = value & cls.__compare_mask__
        else:
            try:
                other = int(other)
            except TypeError:
                other = int(cls(other)) & cls.__compare_mask__
                value = value & cls.__compare_mask__
        return value, other

    def __lt__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__lt__(value, other)

    def __le__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__le__(value, other)

    def __eq__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__eq__(value, other)

    def __ne__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__ne__(value, other)

    def __gt__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__gt__(value, other)

    def __ge__(self, other):
        value, other = self._normalize_for_compare(self.__value__, other)
        return int.__ge__(value, other)

    def __hash__(self):
        return int.__hash__(self.__value__ & type(self).__compare_mask__)

    def __bool__(self):
        return int.__bool__(self.__value__ & type(self).__compare_mask__)

    def __add__(self, other):
        return int.__add__(self.__value__, other)

    def __sub__(self, other):
        return int.__sub__(self.__value__, other)

    def __mul__(self, other):
        return int.__mul__(self.__value__, other)

    def __truediv__(self, other):
        return int.__truediv__(self.__value__, other)

    def __floordiv__(self, other):
        return int.__floordiv__(self.__value__, other)

    def __mod__(self, other):
        return int.__mod__(self.__value__, other)

    def __divmod__(self, other):
        return int.__divmod__(self.__value__, other)

    def __pow__(self, other, *args):
        return int.__pow__(self.__value__, other, *args)

    def __lshift__(self, other):
        return int.__lshift__(self.__value__, other)

    def __rshift__(self, other):
        return int.__rshift__(self.__value__, other)

    def __and__(self, other):
        return int.__and__(self.__value__, other)

    def __xor__(self, other):
        return int.__xor__(self.__value__, other)

    def __or__(self, other):
        return int.__or__(self.__value__, other)

    def __radd__(self, other):
        return int.__radd__(self.__value__, other)

    def __rsub__(self, other):
        return int.__rsub__(self.__value__, other)

    def __rmul__(self, other):
        return int.__rmul__(self.__value__, other)

    def __rtruediv__(self, other):
        return int.__rtruediv__(self.__value__, other)

    def __rfloordiv__(self, other):
        return int.__rfloordiv__(self.__value__, other)

    def __rmod__(self, other):
        return int.__rmod__(self.__value__, other)

    def __rdivmod__(self, other):
        return int.__rdivmod__(self.__value__, other)

    def __rpow__(self, other, *args):
        return int.__rpow__(self.__value__, other, *args)

    def __rlshift__(self, other):
        return int.__rlshift__(self.__value__, other)

    def __rrshift__(self, other):
        return int.__rrshift__(self.__value__, other)

    def __rand__(self, other):
        return int.__rand__(self.__value__, other)

    def __rxor__(self, other):
        return int.__rxor__(self.__value__, other)

    def __ror__(self, other):
        return int.__ror__(self.__value__, other)

    def __iadd__(self, other):
        return self.__value__ + other

    def __isub__(self, other):
        return self.__value__ - other

    def __imul__(self, other):
        return self.__value__ * other

    def __itruediv__(self, other):
        return self.__value__ / other

    def __ifloordiv__(self, other):
        return self.__value__ // other

    def __imod__(self, other):
        return self.__value__ % other

    def __ilshift__(self, other):
        return self.__value__ << other

    def __irshift__(self, other):
        return self.__value__ >> other

    def __iand__(self, other):
        return self.__value__ & other

    def __ixor__(self, other):
        return self.__value__ ^ other

    def __ior__(self, other):
        return self.__value__ | other

    def __neg__(self):
        return -self.__value__

    def __pos__(self):
        return self.__value__

    def __abs__(self):
        return self.__value__

    def __invert__(self):
        return ~self.__value__

    def __int__(self):
        return self.__value__

    def __float__(self):
        return int.__float__(self.__value__)

    def __index__(self):
        return int.__index__(self.__value__)

    def __round__(self, *args):
        return int.__round__(self.__value__, *args)

    def asdict(self):
        """Return bit field values in dictionary form.

        :returns: bit field names/values
        :rtype: dict

        """
        return {name: getattr(self, name) for name in self.__fields__}

    def update(self, *args, **kwargs):
        """update bit fields.

        ``D.update([E, ]**F)`` -> ``None``

        Update bit fields in "D" from dict/iterable E and F.

        - If E is present and has a .keys() method, then does:  for k in E: D.k = E[k]
        - If E is present and lacks a .keys() method, then does:  for k, v in E: D.k. = v
        - In either case, this is followed by: for k in F:  D.k = F[k]

        """
        updates = {}
        updates.update(*args, **kwargs)

        for name, value in updates.items():
            setattr(self, name, value)

    def __setattr__(self, key, value):
        if key.startswith('__') or key in self.__fields__:
            super(BitFields, self).__setattr__(key, value)
        else:
            raise AttributeError(f'{type(self).__name__!r} has no attribute {key!r}')
