# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as big endian floating point number."""

from ._float import Float


class Float32(Float, nbytes=4, byteorder='big'):

    """Big endian single precision floating point number."""


class Float64(Float, nbytes=8, byteorder='big'):
    """Big endian single precision floating point number."""


del Float
