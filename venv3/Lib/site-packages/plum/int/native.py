# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as native endian integer number."""

import sys

# pylint: disable=wildcard-import, unused-wildcard-import

if sys.byteorder == 'little':
    from .little import *
else:
    from .big import *
