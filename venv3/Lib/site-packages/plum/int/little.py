# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Little endian integer types."""

from ._int import Int


class SInt8(Int, nbytes=1, signed=True, byteorder='little'):

    """Signed little endian 8 bit integer."""


class SInt16(Int, nbytes=2, signed=True, byteorder='little'):

    """Signed little endian 16 bit integer."""


class SInt32(Int, nbytes=4, signed=True, byteorder='little'):

    """Signed little endian 32 bit integer."""


class SInt64(Int, nbytes=8, signed=True, byteorder='little'):

    """Signed little endian 64 bit integer."""


class UInt8(Int, nbytes=1, signed=False, byteorder='little'):

    """Unsigned little endian 8 bit integer."""


class UInt16(Int, nbytes=2, signed=False, byteorder='little'):

    """Unsigned little endian 16 bit integer."""


class UInt32(Int, nbytes=4, signed=False, byteorder='little'):

    """Unsigned little endian 32 bit integer."""


class UInt64(Int, nbytes=8, signed=False, byteorder='little'):

    """Unsigned little endian 64 bit integer."""


del Int
