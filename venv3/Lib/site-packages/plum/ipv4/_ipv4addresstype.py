# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Integer type metaclass."""

from .._plumtype import PlumType


class IpV4AddressType(PlumType):

    """IPV4 address metaclass.

    Create custom IpV4Address subclass.

    :param str byteorder: ``'big'`` or ``'little'``

    """

    def __new__(mcs, name, bases, namespace, byteorder=None):
        # pylint: disable=too-many-arguments, unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, byteorder=None):
        # pylint: disable=too-many-arguments
        super().__init__(name, bases, namespace)

        if byteorder is None:
            byteorder = cls.__byteorder__

        assert byteorder in {'big', 'little'}

        # store byteorder, nbytes, signed separately for use later
        # to pack/unpack to be able to support any sized integer
        # (versus storing struct pack/unpack function similar to
        # float type which is restricted to common sizes).

        cls.__byteorder__ = byteorder
        cls.__little_endian__ = byteorder == 'little'
        cls.__nbytes__ = 4

        # FUTURE - int fast unpack should work, need special fast pack
        #
        # if boost:
        #     unpack_as_int = False
        #     strict_enum = False
        #     signed = False
        #     # attach binary string containing plum-c accelerator "C" structure
        #     # (so structure memory de-allocated when class deleted)
        #     cls.__plum_boost_internals__ = boost.fastint.add_c_acceleration(
        #         cls, cls.__nbytes__, byteorder == 'little', signed,
        #         unpack_as_int, strict_enum)
