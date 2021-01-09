# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""BitFields type metaclass."""

from ..._plumtype import PlumType
from ._bitfield import BitField


class MockBitFields:

    """Fake BitFields type for calculating default value."""

    def __init__(self, value):
        self.__value__ = value

    def __int__(self):
        return self.__value__


class BitFieldsType(PlumType):

    """BitFields type metaclass.

    Create custom |BitFields| subclass. For example:

    :param int nbytes: number of bytes
    :param str byteorder: ``'big'`` or ``'little'``
    :param int default: default value (before applying bit field values)
    :param int ignore: mask applied during comparison to ignore bit fields

    For example:

        >>> from plum.int.bitfields import BitFields, BitField
        >>> class MyBits(BitFields, nbytes=1, byteorder='big', default=0, ignore=0x80):
        ...     nibble: int = BitField(pos=0, size=4)
        ...     threebits: int = BitField(pos=4, size=3)
        ...
        >>>

    """

    def __new__(mcs, name, bases, namespace, nbytes=None, byteorder=None,
                default=None, ignore=None):
        # pylint: disable=too-many-arguments,unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, byteorder=None,
                 default=None, ignore=None):
        # pylint: disable=too-many-arguments, too-many-locals
        # pylint: disable=too-many-branches, too-many-statements
        super().__init__(name, bases, namespace)

        # validate bit field class attributes

        annotations = getattr(cls, '__annotations__', {})

        fields = {}
        for fieldname, bitfield in namespace.items():
            if not isinstance(bitfield, BitField):
                continue

            bitfield.finish_initialization(fieldname, annotations)

            fields[fieldname] = bitfield

        # fill in missing positions

        pos = 0
        for field in fields.values():
            if field.pos is None:
                field.pos = pos
            pos = field.pos + field.size

        # check for overlap

        claimed_bits = {}
        for fieldname, field in fields.items():
            for i in range(field.pos, field.pos + field.size):
                if i in claimed_bits:
                    raise TypeError(
                        f'bit field {fieldname!r} overlaps with {claimed_bits[i]!r}')

                claimed_bits[i] = fieldname

        # default/validate 'nbytes'

        if fields:
            numbits = max(field.pos + field.size for field in fields.values())
            nbytes_needed = 1
            while numbits > (nbytes_needed * 8):
                nbytes_needed *= 2
        else:
            nbytes_needed = 1

        if nbytes is None:
            nbytes = nbytes_needed
        else:
            nbytes = int(nbytes)
            if nbytes < nbytes_needed:
                raise TypeError(
                    f'nbytes must be at least {nbytes_needed} for bitfields specified')

        max_ = (1 << (nbytes * 8)) - 1

        # default/validate 'byteorder'

        if byteorder is None:
            byteorder = cls.__byteorder__

        if byteorder not in {'big', 'little'}:
            raise ValueError('byteorder must be either "big" or "little"')

        # validate 'default' and blend in defaults from individual fields

        if default is None:
            default = cls.__default__

        default = int(default)

        if not 0 <= default <= max_:
            raise ValueError(f'default must be: 0 <= number <= 0x{max_:x}')

        blended_default = MockBitFields(default)
        for field in fields.values():
            if field.default is not None:
                field.__set__(blended_default, field.default)

        # validate 'ignore' and blend in ignores from individual fields

        if ignore is None:
            ignore = cls.__ignore__

        ignore = int(ignore)

        if not 0 <= ignore <= max_:
            raise ValueError(f'ignore must be: 0 <= number <= 0x{max_:x}')

        for field in fields.values():
            if field.ignore:
                ignore |= field.mask << field.pos
            elif isinstance(field.cls, BitFieldsType):
                ignore |= field.cls.__ignore__ << field.pos

        cls.__byteorder__ = byteorder
        cls.__compare_mask__ = (max_ ^ ignore) & max_
        cls.__fields__ = fields
        cls.__default__ = int(blended_default)
        cls.__fields_with_defaults__ = {
            name for name, field in fields.items() if field.default is not None}
        cls.__ignore__ = ignore
        cls.__max__ = max_
        cls.__nbytes__ = nbytes
