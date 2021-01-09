# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Type map structure member definition."""

from ._member import Member


class TypeMember(Member):

    """Structure member holding a type map for another member.

    :param dict mapping: type member value (key) to Plum type (value) mapping
    :param PlumType cls: member type
    :param bool ignore: ignore member during comparisons
    :param function decipher:

    """

    __slots__ = [
        'cls',
        'decipher',
        'default',
        'ignore',
        'index',
        'mapping',
        'name',
        'reversed_mapping',
        'variable_type_member_index',
        'variable_type_member_name',
    ]

    def __init__(self, *, mapping, cls=None, ignore=False):
        super(TypeMember, self).__init__(cls=cls, default=self.get_type_value, ignore=ignore)
        self.mapping = mapping
        self.reversed_mapping = {value: key for key, value in self.mapping.items()}
        # filled in by VariableTypeMember definition adjustments
        self.variable_type_member_index = None
        self.variable_type_member_name = None

    def get_type_value(self, structure):
        """Determine structure type member value from variably typed structure member.

        :param Structure structure: parent structure
        :returns: structure type member value (adjusted by ratio)
        :rtype: object

        """
        variable_type_member = structure[self.variable_type_member_index]

        member_type = type(variable_type_member)

        try:
            return self.reversed_mapping[member_type]
        except KeyError:
            types = [c.__name__ for c in self.reversed_mapping]
            raise TypeError(
                f'structure member {self.variable_type_member_name!r} must '
                f'be one of the following types: {types}, not {member_type.__name__!r}')

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """
        if self.variable_type_member_name is None:
            raise TypeError(
                f"{self.name!r} member never associated with a variable type member")
