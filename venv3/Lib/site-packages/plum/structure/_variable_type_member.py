# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Variable type structure member definition."""

from ._member import Member
from ._type_member import TypeMember


class VariableTypeMember(Member):

    """Variable type member definition.

    :param TypeMember type_member: type map member definition
    :param object default: initial value when unspecified
    :param bool ignore: ignore member during comparisons

    """

    __slots__ = [
        'cls',
        'default',
        'ignore',
        'index',
        'name',
        'type_member',
    ]

    def __init__(self, *, type_member, default=None, ignore=False):
        if not isinstance(type_member, TypeMember):
            raise TypeError("invalid 'type_member', must be a 'TypeMember' instance")

        # pylint: disable=unidiomatic-typecheck
        if default is not None and type(default) not in type_member.mapping.values():
            raise TypeError(
                "invalid default type, type must in 'mapping'")

        super(VariableTypeMember, self).__init__(
            cls=self.get_type, default=default, ignore=ignore,
            setter=self.set_structure_value)

        self.type_member = type_member

    def get_type(self, structure):
        """Get structure variably typed member type.

        :param Structure structure: parent structure
        :returns: variably typed member type
        :rtype: Plum

        """
        return self.type_member.mapping[structure[self.type_member.index]]

    def set_structure_value(self, structure, value):
        """Set structure variable type member and update structure type member.

        Set new value in structure variably typed member. Set associated structure
        type member with value to reflect type of new value.

        """
        structure[self.index] = value
        structure[self.type_member.index] = self.type_member.default(structure)

    def adjust_members(self, members):
        """Perform adjustment to other members.

        :param dict members: structure member definitions

        """
        self.type_member.variable_type_member_index = self.index
        self.type_member.variable_type_member_name = self.name
