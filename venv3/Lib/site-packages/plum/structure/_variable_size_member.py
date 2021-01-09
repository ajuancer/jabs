# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Variable sized member definition."""

from .._plum import Plum, PlumType
from .._exceptions import ExcessMemoryError
from .._plum import getbytes
from ._member import Member
from ._size_member import SizeMember


class VariablySizedMember(Plum, metaclass=PlumType):

    """Variably sized member."""

    __member_cls__ = Plum
    __offset__ = 0
    __ratio__ = 1
    __size_member_index__ = 0

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        # pylint: disable=too-many-locals

        member_cls = cls.__member_cls__

        if dump:
            dump.cls = member_cls

        expected_size_in_bytes = (
            parent[cls.__size_member_index__] - cls.__offset__) * cls.__ratio__

        chunk, offset = getbytes(buffer, offset, expected_size_in_bytes, dump)

        if dump:
            dump.memory = b''

        item, actual_size_in_bytes = member_cls.__unpack__(chunk, 0, parent, dump)

        extra_bytes = chunk[actual_size_in_bytes:]

        if extra_bytes:
            if dump:
                for i in range(0, len(extra_bytes), 16):
                    if i:
                        dump.add_record(memory=extra_bytes[i:i+16])
                    else:
                        dump.add_record(
                            separate=True, value='<excess bytes>',
                            memory=extra_bytes[i:i+16])

            raise ExcessMemoryError(f'{len(extra_bytes)} unconsumed bytes', extra_bytes)

        return item, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        member_cls = cls.__member_cls__

        if dump:
            dump.cls = member_cls

        return member_cls.__pack__(buffer, offset, parent, value, dump)


class VariableSizeMember(Member):

    """Variable sized member definition.

    :param SizeMember size_member: size member definition
    :param Plum cls: member type (or factory function)
    :param object default: initial value when unspecified
    :param bool ignore: ignore member during comparisons

    """

    __slots__ = [
        'cls',
        'default',
        'ignore',
        'index',
        'name',
        'setter',
        'size_member',
    ]

    def __init__(self, *, size_member, cls=None, default=None, ignore=False):
        if not isinstance(size_member, SizeMember):
            raise TypeError("invalid 'size_member', must be a 'SizeMember' instance")
        super(VariableSizeMember, self).__init__(
            cls=cls, default=default, ignore=ignore, setter=self.set_structure_value)
        self.size_member = size_member

    def adjust_members(self, members):
        """Perform adjustment to other members.

        :param dict members: structure member definitions

        """
        self.size_member.variable_size_member_cls = self.cls
        self.size_member.variable_size_member_index = self.index

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """
        namespace = {
            '__member_cls__': self.cls,
            '__offset__': self.size_member.offset,
            '__ratio__': self.size_member.ratio,
            '__size_member_index__': self.size_member.index,
        }

        self.cls = type('VariablySizedMember', (VariablySizedMember, ), namespace)

    def set_structure_value(self, structure, value):
        """Set structure array member and update structure dimensions member.

        Set new value in structure array member. Set structure dimensions member
        with dimensions of new value.

        """
        structure[self.index] = value
        structure[self.size_member.index] = self.size_member.default(structure)
