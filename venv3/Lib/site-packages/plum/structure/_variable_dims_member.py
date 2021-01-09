# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Variable dimensions array structure member definition."""

from .._plum import Plum, PlumType
from ..array import Array
from ..int import Int
from ._member import Member
from ._dims_member import DimsMember


class VariableDimArray(Plum, metaclass=PlumType):

    """Variably sized single dimension array."""

    __array_cls__ = Array
    __dims_member_index__ = 0
    __single_dim__ = True

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        array_cls = cls.__array_cls__

        try:
            array_cls = array_cls.__cls_factory__
        except AttributeError:
            pass
        else:
            array_cls = array_cls(parent)

        if dump:
            dump.cls = array_cls

        if cls.__single_dim__:
            dims = (int(parent[cls.__dims_member_index__]), )
        else:
            dims = tuple(int(d) for d in parent[cls.__dims_member_index__])

        # None -> no parent
        return array_cls.__unpack__(buffer, offset, None, dump, dims)

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        # pylint: disable=arguments-differ
        array_cls = cls.__array_cls__

        try:
            array_cls = array_cls.__cls_factory__
        except AttributeError:
            pass
        else:
            array_cls = array_cls(parent)

        if dump:
            dump.cls = array_cls

        if cls.__single_dim__:
            dims = (int(parent[cls.__dims_member_index__]), )
        else:
            dims = tuple(int(d) for d in parent[cls.__dims_member_index__])

        return array_cls.__pack__(buffer, offset, parent, value, dump, dims)


class VariableDimsMember(Member):

    """Variable dimensions array structure member definition.

    :param DimsMember dims_member: array dimensions member name
    :param Plum cls: undimensioned array base class (or factory function)
    :param object default: initial value when unspecified
    :param bool ignore: ignore member during comparisons

    """

    __slots__ = [
        'cls',
        'default',
        'dims_member',
        'ignore',
        'index',
        'name',
        'setter',
    ]

    def __init__(self, *, dims_member, cls=None, default=None, ignore=False):
        if not isinstance(dims_member, DimsMember):
            raise TypeError("invalid 'dims_member', must be a 'DimsMember' instance")

        self.dims_member = dims_member

        super(VariableDimsMember, self).__init__(
            cls=cls, default=default, ignore=ignore, setter=self.set_structure_value)

    def adjust_members(self, members):
        """Perform adjustment to other members.

        :param dict members: structure member definitions

        """
        self.dims_member.array_member_index = self.index

    def finalize(self, members):
        """Perform final adjustments.

        :param dict members: structure member definitions

        """
        dims_cls = self.dims_member.cls

        namespace = {
            '__array_cls__': self.cls,
            '__dims_member_index__': self.dims_member.index,
            '__single_dim__': issubclass(dims_cls, Int),
        }

        self.cls = type('Varies', (VariableDimArray, ), namespace)

    def set_structure_value(self, structure, value):
        """Set structure array member and update structure dimensions member.

        Set new value in structure array member. Set structure dimensions member
        with dimensions of new value.

        """
        structure[self.index] = value
        structure[self.dims_member.index] = self.dims_member.default(structure)
