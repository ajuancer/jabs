# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Collection of uniquely typed items."""

from plum._plum import Plum, PlumType


class Items(list, Plum, metaclass=PlumType):

    """Collection of uniquely typed items.

    :param iterable iterable: items

    """

    __nbytes__ = None

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        parent = None

        for i, item in enumerate(value):
            item_cls = type(item)

            subdump = None if dump is None else dump.add_record(access=f'[{i}]', cls=item_cls)

            if not issubclass(item_cls, Plum):
                if subdump:
                    subdump.value = repr(item)
                    subdump.cls = item_cls.__name__ + ' (invalid)'

                raise TypeError(f'item {i} not a plum type')

            offset = item_cls.__pack__(buffer, offset, parent, item, subdump)

        return offset

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        raise TypeError(f'{cls.__name__!r} does not support unpacking')

    def __repr__(self):
        return f'{type(self).__name__}({list.__repr__(self)})'
