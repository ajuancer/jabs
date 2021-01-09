# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Array type metaclass."""

from functools import reduce
from operator import mul

from .._plum import Plum, SizeError
from .._plumtype import PlumType

GREEDY_DIMS = (None,)


class ArrayInitError(Exception):

    """Array initialization error."""


class ArrayType(PlumType):

    """Array type metaclass.

    Create custom |Array| subclass.

    :param PlumType item_cls: array item type
    :param dims: array dimension
    :type dims: tuple of int or None

     For example:

            >>> from plum.array import Array
            >>> from plum.int.little import UInt16
            >>> class MyArray(Array, item_cls=UInt16, dims=(10,)):
            ...     pass
            ...
            >>>

    """

    def __new__(mcs, name, bases, namespace, item_cls=None, dims=None):
        # pylint: disable=too-many-arguments, unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, item_cls=None, dims=None):
        # pylint: disable=too-many-arguments
        super().__init__(name, bases, namespace)

        if item_cls is None:
            item_cls = cls.__item_cls__

        assert issubclass(item_cls, Plum)

        if dims is None:
            dims = cls.__dims__

        dims = tuple(None if d is None else int(d) for d in dims)
        assert all(True if d is None else d > 0 for d in dims)

        if None in dims:
            nbytes = None
        else:
            try:
                nbytes = item_cls.nbytes
            except SizeError:
                nbytes = None
            else:
                nbytes *= reduce(mul, dims)

        cls.__dims__ = dims
        cls.__item_cls__ = item_cls
        cls.__nbytes__ = nbytes

    def __call__(cls, iterable=None, _dims_indices_name=None):
        try:
            dims, indices, clsname = _dims_indices_name
        except TypeError:
            # must be None
            dims, indices, clsname = list(cls.__dims__), tuple(), cls.__name__

        this_dim, *item_dims = dims

        item_cls = cls if item_dims else cls.__item_cls__

        if iterable is None:
            if this_dim is None:
                iterable = []
            elif item_dims:
                iterable = [None] * this_dim
            else:
                iterable = [item_cls() for _ in range(this_dim)]

        array = list.__new__(cls, iterable)
        list.__init__(array, iterable)
        array.__class_name__ = clsname  # for repr

        if this_dim is not None and len(array) != this_dim:
            index = f"[{']['.join(str(i) for i in indices)}]" if indices else ''

            invalid_dimension = (
                f'expected length of item{index} to be {this_dim} '
                f'but instead found {len(array)}')

            raise ArrayInitError(invalid_dimension)

        if item_dims:
            # for multi dimensional arrays, create array instances for each
            # dimension to report improper dimensions and fill in default values
            array[:] = [item_cls.__call__(item, (item_dims, indices + (i, ), None))
                        for i, item in enumerate(array)]

        return array
