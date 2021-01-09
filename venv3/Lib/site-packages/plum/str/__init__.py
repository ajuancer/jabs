# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as a string."""

from ._str import Str
from ._strtype import StrType


class AsciiStr(Str, encoding='ascii'):

    """Interpret bytes as ASCII encoded string."""


class AsciiZeroTermStr(Str, encoding='ascii', zero_termination=True):

    """Interpret bytes as ASCII encoded zero terminated string."""


class Utf8Str(Str, encoding='utf-8'):

    """Interpret bytes as UTF-8 encoded string."""


class Utf8ZeroTermStr(Str, encoding='utf-8', zero_termination=True):

    """Interpret bytes as UTF-8 encoded zero terminated string."""
