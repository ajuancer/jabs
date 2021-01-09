# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Array dimension structure member definition."""

from ._member import Member
from ..int import Int


class DimsMember(Member):

    """Array dimension structure member definition.

    :param Plum cls: member type
    :param bool ignore: ignore member during comparisons

    """

    __slots__ = [
        'default',
        'name',
        'cls',
        'ignore',
        'index',
        'array_member_index',
        'setter',
    ]

    def __init__(self, *, cls=None, ignore=False):
        super(DimsMember, self).__init__(cls=cls, ignore=ignore)
        if issubclass(cls, Int):
            self.default = self.calculate_dim
        else:
            self.default = self.calculate_dims
        self.array_member_index = None  # filled in by VariableDimsMember

    def calculate_dim(self, structure):
        """Determine dimension from structure one-dimensional array value.

        :param Structure structure: parent structure
        :returns: array dimension
        :rtype: int

        """
        return len(structure[self.array_member_index])

    def calculate_dims(self, structure):
        """Determine dimensions from structure multi-dimensional array value.

        :param Structure structure: parent structure
        :returns: array dimensions
        :rtype: list of int

        """
        array = structure[self.array_member_index]
        dims = []
        for _ in range(self.cls.__dims__[0]):
            dims.append(len(array))
            array = array[0]

        return dims

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """
        if self.array_member_index is None:
            raise TypeError(
                f"{self.name!r} member never associated with a variable dims array member")
