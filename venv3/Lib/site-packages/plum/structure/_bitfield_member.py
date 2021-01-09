# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Bit field structure member definition."""

from plum.int.bitfields import BitFields
from plum.structure._member import Member


class BitFieldMember(Member):

    """Bit field structure member definition.

    :param BitFields cls: BitFields class that incorporates member
    :param object default: initial value when unspecified

    """

    __slots__ = [
        'cls',
        'default',
        'ignore',
        'index',
        'name',
    ]

    def __init__(self, *, cls, default=None):
        if not issubclass(cls, BitFields):
            raise TypeError("'cls' must be a 'BitFields' subclass")
        super(BitFieldMember, self).__init__(cls=cls, default=default)

    def __get__(self, structure, structure_cls):
        return getattr(structure[self.index], self.name)

    def __set__(self, structure, value):
        setattr(structure[self.index], self.name, value)

    def get_accessor(self):
        """Member accessor.

        :returns: descriptor protocol accessor
        :rtype: Member or property

        """
        return self
