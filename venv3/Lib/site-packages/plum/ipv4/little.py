# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as little endian IPV4 address."""

from plum.ipv4._ipv4address import IpV4Address as IpV4AddressBase


class IpV4Address(IpV4AddressBase):

    """IPV4 Address, little endian format."""


del IpV4AddressBase
