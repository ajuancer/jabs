# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Integer flag type metaclass."""

from ..enum import EnumType


class FlagType(EnumType):

    """Integer flag type metaclass.

    Create custom |Flag| subclass.

    :param int nbytes: number of bytes
    :param str byteorder: ``'big'`` or ``'little'``
    :param EnumMeta source: enumeration to copy

    For example:

        >>> from plum.int.flag import Flag
        >>> class MyFlags(Flag, nbytes=1, byteorder='little'):
        ...     RED = 1
        ...     GREEN = 2
        ...     BLUE = 4
        ...
        >>>

    """

    @classmethod
    def __prepare__(mcs, name, bases, nbytes=None, byteorder=None, source=None):
        # pylint: disable=arguments-differ
        # pylint: disable=unused-argument
        # pylint: disable=too-many-arguments
        namespace = super().__prepare__(name, bases)

        if source is not None:
            for member in source:
                namespace[member.name] = member.value

        return namespace

    def __new__(mcs, name, bases, namespace, nbytes=None, byteorder=None, source=None):
        # pylint: disable=signature-differs
        # pylint: disable=too-many-arguments
        return super().__new__(mcs, name, bases, namespace,
                               nbytes=nbytes, byteorder=byteorder, signed=False)

    def __init__(cls, name, bases, namespace, nbytes=None, byteorder=None, source=None):
        # pylint: disable=too-many-arguments,unused-argument
        super().__init__(name, bases, namespace,
                         nbytes=nbytes, byteorder=byteorder, signed=False)
