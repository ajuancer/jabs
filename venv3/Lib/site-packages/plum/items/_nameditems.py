# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Collection of uniquely typed named items."""

from plum._plum import Plum, PlumType


class NamedItems(dict, Plum, metaclass=PlumType):

    """Collection of uniquely typed named items.

    :param iterable: items
    :type: dict or list of key/values pairs
    :param dict kwargs: items

    """

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        parent = None

        for i, (name, item) in enumerate(value.items()):
            item_cls = type(item)

            subdump = None if dump is None else dump.add_record(
                access=f'[{i}] (.{name})', cls=item_cls)

            if not issubclass(item_cls, Plum):
                if subdump:
                    subdump.value = repr(item)
                    subdump.cls = item_cls.__name__ + ' (invalid)'
                raise TypeError(f'item {name!r} not a plum type')

            offset = item_cls.__pack__(buffer, offset, parent, item, subdump)

        return offset

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        raise TypeError(f'{cls.__name__!r} does not support unpacking')

    def __repr__(self):
        return f'{type(self).__name__}({dict.__repr__(self)})'

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            # for consistent error message, let standard mechanism raise the exception
            object.__getattribute__(self, name)
