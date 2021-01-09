# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Structure type."""

from enum import Enum

from .._plum import Plum
from .._plumview import PlumView
from ._structuretype import StructureType, NO_MEMBERS_DEFINED
from ._structureview import StructureView


class Structure(list, Plum, metaclass=StructureType):

    """Interpret bytes as a list of uniquely typed items.

    :param iterable iterable: items

    """

    # filled in by metaclass
    __ignore_flags__ = ()
    __names_types__ = NO_MEMBERS_DEFINED  # names, types
    __nbytes__ = 0
    __offsets__ = ()

    def __init__(self, *args, **kwargs):
        # pylint: disable=super-init-not-called
        raise TypeError(f'{type(self).__name__!r} class may not be instantiated')

    def asdict(self):
        """Return structure members in dictionary form.

        :returns: structure members
        :rtype: dict

        """
        names, _types = self.__names_types__
        return dict(zip(names, self))

    @classmethod
    def __pack__(cls, buffer, offset, parent, value, dump):
        # pylint: disable=too-many-branches,unused-argument
        names, types = cls.__names_types__

        if isinstance(value, PlumView):
            # read all members at once
            value = value.get()

        if isinstance(value, dict):
            value = cls(**value)

        try:
            if len(names) != len(value):
                raise ValueError(
                    f'invalid value, '
                    f'{cls.__name__!r} pack expects an iterable of length {len(names)}, '
                    f'got an iterable of length {len(value)}')
        except TypeError:
            raise TypeError(
                f'invalid value, '
                f'{cls.__name__!r} pack expects an iterable of length {len(names)}, '
                f'got a non-iterable')

        if dump:
            for i, (name, value_cls) in enumerate(zip(names, types)):
                offset = value_cls.__pack__(
                    buffer, offset, value, value[i],
                    dump.add_record(access=f'[{i}] (.{name})', cls=value_cls))
        else:
            for i, value_cls in enumerate(types):
                offset = value_cls.__pack__(buffer, offset, value, value[i], None)

        return offset

    @classmethod
    def __unpack__(cls, buffer, offset, parent, dump):
        # pylint: disable=too-many-locals,unused-argument
        names, types = cls.__names_types__

        self = list.__new__(cls)
        append = list.append

        if dump:
            for i, (name, item_cls) in enumerate(zip(names, types)):
                item, offset = item_cls.__unpack__(
                    buffer, offset, self,
                    dump.add_record(access=f'[{i}] (.{name})', cls=item_cls))
                append(self, item)
        else:
            for item_cls in types:
                item, offset = item_cls.__unpack__(buffer, offset, self, dump)
                append(self, item)

        return self, offset

    def __eq__(self, other):
        if isinstance(other, type(self)) and self.__ignore_flags__:
            for self_item, other_item, ignore in zip(self, other, self.__ignore_flags__):
                if not ignore and self_item != other_item:
                    return False
            return True

        return super(Structure, self).__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __setattr__(self, name, value):
        # get the attribute to raise an exception if invalid name
        getattr(self, name)
        object.__setattr__(self, name, value)

    def __repr__(self):
        names, _types = self.__names_types__
        reprs = [str(value) if isinstance(value, Enum) else repr(value) for value in self]
        lst = [value if name is None else name + '=' + value
               for name, value in zip(names, reprs)]
        return f"{type(self).__name__}({', '.join(lst)})"

    @classmethod
    def __view__(cls, buffer, offset=0):
        """Create plum view of bytes buffer.

        :param buffer: bytes buffer
        :type buffer: bytes-like (e.g. bytes, bytearray, memoryview)
        :param int offset: byte offset

        """
        if not cls.__nbytes__:
            raise TypeError(f"cannot create view for structure {cls.__name__!r} "
                            "with variable size")

        return StructureView(cls, buffer, offset)


# register Structure as base class so that meta class can determine if
# methods have been overridden so as to not generate them
StructureType.structure_class = Structure
