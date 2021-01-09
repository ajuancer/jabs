# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Interpret bytes as a list of uniformly typed items."""

from .._plum import Plum, getbytes
from ..int.little import UInt8
from ._arraytype import ArrayType, GREEDY_DIMS


class Array(list, Plum, metaclass=ArrayType):

    """Interpret bytes as a list of uniformly typed items.

    :param iterable iterable: items

    """

    # filled in by metaclass
    __dims__ = GREEDY_DIMS
    __item_cls__ = UInt8
    __nbytes__ = None
    __class_name__ = None

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump, dims=None):
        # pylint: disable=too-many-branches,too-many-locals,
        # pylint: disable=too-many-arguments,arguments-differ
        parent = None

        if dims is None:
            dims = cls.__dims__

        array = list()

        if dims == GREEDY_DIMS:
            # get remainder of memory bytes
            # (no dump so memory bytes aren't recorded)
            chunk, offset = getbytes(buffer, offset)

            item_cls = cls.__item_cls__

            _offset = 0
            _len_chunk = len(chunk)

            i = 0
            while _offset < _len_chunk:
                item, _offset, = item_cls.__unpack__(
                    chunk, _offset, parent,
                    None if dump is None else dump.add_record(
                        access=f'[{i}]', cls=item_cls))
                array.append(item)
                i += 1

        elif None in dims:
            raise TypeError(
                'greedy multidimensional array types do not support unpack operation')
        else:
            this_dim, *item_dims = dims

            if item_dims:
                for i in range(this_dim):
                    item, offset = cls.__unpack__(
                        buffer, offset, parent,
                        None if dump is None else dump.add_record(access=f'[{i}]'),
                        item_dims)

                    array.append(item)
            else:
                item_cls = cls.__item_cls__

                for i in range(this_dim):
                    item, offset = item_cls.__unpack__(
                        buffer, offset, parent,
                        None if dump is None else dump.add_record(
                            access=f'[{i}]', cls=item_cls))

                    array.append(item)

        return array, offset

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump, dims=None):
        # pylint: disable=too-many-arguments, arguments-differ, too-many-branches

        parent = None

        this_dim, *item_dims = cls.__dims__ if dims is None else dims

        try:
            actual_length = len(value)
        except TypeError:
            if dump:
                dump.value = value
            raise TypeError(
                f'invalid value, expected iterable of '
                f'{"any " if this_dim is None else ""}'
                f'length{"" if this_dim is None else " " + str(this_dim)}'
                f', got non-iterable')

        if this_dim is not None and actual_length != this_dim:
            if dump:
                for i, item in enumerate(value):
                    dump.add_record(access=f'[{i}]', value=item, separate=(i == this_dim))
            raise TypeError(
                f'invalid value, expected iterable of '
                f'{this_dim} length, got iterable of length {actual_length}')

        if item_dims:
            for i, item in enumerate(value):
                offset = cls.__pack__(
                    buffer, offset, parent, item,
                    None if dump is None else dump.add_record(access=f'[{i}]'),
                    item_dims)
        else:
            item_cls = cls.__item_cls__

            for i, item in enumerate(value):
                offset = item_cls.__pack__(
                    buffer, offset, parent, item,
                    None if dump is None else dump.add_record(
                        access=f'[{i}]', cls=item_cls))

        return offset

    def __str__(self):
        return list.__repr__(self)

    def __repr__(self):
        rep = list.__repr__(self)

        if self.__class_name__:
            rep = f'{self.__class_name__}({rep})'

        return rep
