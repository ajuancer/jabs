# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Float type view."""

from numbers import Real

from .._plumview import NumberView


class FloatView(NumberView, Real):

    """Float type view."""

    __float__ = NumberView.get
