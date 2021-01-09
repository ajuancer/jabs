# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Size structure member definition."""

from .. import pack
from ._member import Member


class SizeMember(Member):

    """Size structure member definition.

    :param Plum cls: member type
    :param int ratio: number of bytes per increment of member
    :param int offset: difference in size (in bytes)
    :param bool ignore: ignore member during comparisons

    """

    __slots__ = [
        'cls',
        'default',
        'ignore',
        'index',
        'name',
        'offset',
        'ratio',
        'setter',
        'variable_size_member_cls',
        'variable_size_member_index',
    ]

    def __init__(self, *, cls=None, ratio=1, offset=0, ignore=False):
        super(SizeMember, self).__init__(
            cls=cls, ignore=ignore, default=self.calculate_size)
        self.ratio = ratio
        self.offset = offset
        # filled in by VariableSizeMember definition adjustments
        self.variable_size_member_cls = None
        self.variable_size_member_index = None

    def calculate_size(self, structure):
        """Calculate structure size member value from variably sized structure member.

        :param Structure structure: parent structure
        :returns: structure size member value (adjusted by ratio and offset)
        :rtype: int

        """
        sized_object = structure[self.variable_size_member_index]

        # pylint: disable=isinstance-second-argument-not-valid-type
        if isinstance(sized_object, self.variable_size_member_cls):
            size = sized_object.nbytes // self.ratio
        else:
            size = len(pack(self.variable_size_member_cls, sized_object)) // self.ratio

        return size + self.offset

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """
        if self.variable_size_member_index is None:
            raise TypeError(
                f"{self.name!r} member never associated with a variable size member")
