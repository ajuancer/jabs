# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Float type metaclass."""

from struct import Struct

from .._plumtype import PlumType


FORMAT_CODES = {2: 'e', 4: 'f', 8: 'd'}
ENDIAN_CODES = {'big': '>', 'little': '<'}


class FloatType(PlumType):

    """Float type metaclass.

    Create custom |Float| subclass.

    :param int nbytes: number of bytes
    :param str byteorder: ``'big'`` or ``'little'``

    For example:

        >>> from plum.float import Float
        >>> class Float32(Float, nbytes=4, byteorder='big'):
        ...     pass
        ...
        >>>

    """

    def __new__(mcs, name, bases, namespace, nbytes=None, byteorder=None):
        # pylint: disable=unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, byteorder=None):
        super().__init__(name, bases, namespace)

        if nbytes is None:
            nbytes = cls.__nbytes__

        nbytes = int(nbytes)

        assert nbytes in [2, 4, 8]

        if byteorder is None:
            byteorder = cls.__byteorder__

        assert byteorder in {'big', 'little'}

        struct = Struct(ENDIAN_CODES[byteorder] + FORMAT_CODES[nbytes])

        cls.__byteorder__ = byteorder
        cls.__nbytes__ = nbytes
        cls.__struct_pack__ = struct.pack
        cls.__struct_unpack__ = struct.unpack
