# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as little endian floating point number."""

from ._float import Float


class Float32(Float, nbytes=4, byteorder='little'):

    """Big endian single precision floating point number."""


class Float64(Float, nbytes=8, byteorder='little'):
    """Big endian single precision floating point number."""


del Float
