# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""ByteArray type metaclass."""

from .._plumtype import PlumType


class ByteArrayType(PlumType):

    """ByteArray type metaclass.

    Create custom |ByteArray| subclass. For example:

        >>> from plum.bytearray import ByteArray
        >>> class ByteArray1(ByteArray, nbytes=4):
        ...     pass
        ...
        >>>

    :param int nbytes: size in number of bytes
    :param int fill: default value to fill unspecified bytes

    """

    def __new__(mcs, name, bases, namespace, nbytes=None, fill=None):
        # pylint: disable=unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, fill=None):
        super().__init__(name, bases, namespace)

        if nbytes is None:
            nbytes = cls.__nbytes__
        else:
            assert nbytes > 0

        if fill is None:
            fill_tuple = cls.__fill__
        else:
            fill_tuple = (fill, )

        cls.__nbytes__ = nbytes
        cls.__fill__ = fill_tuple
