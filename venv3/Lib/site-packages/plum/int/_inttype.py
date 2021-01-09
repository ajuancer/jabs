# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Integer type metaclass."""

from .. import boost
from .._plumtype import PlumType


class IntType(PlumType):

    """Int type metaclass.

    Create custom |Int| subclass.

    :param int nbytes: number of bytes
    :param bool signed: signed integer
    :param str byteorder: ``'big'`` or ``'little'``
    :param PlumType dref: pointer dereference type

    For example:

        >>> from plum.int import Int
        >>> class SInt24(Int, nbytes=3, signed=True, byteorder='big'):
        ...     pass
        ...
        >>>

    """

    __unpack_int__ = True

    def __new__(mcs, name, bases, namespace, nbytes=None, signed=None, byteorder=None,
                dref=None):
        # pylint: disable=too-many-arguments, unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, nbytes=None, signed=None, byteorder=None,
                 dref=None):
        # pylint: disable=too-many-arguments
        super().__init__(name, bases, namespace)

        if nbytes is None:
            nbytes = cls.__nbytes__

        nbytes = int(nbytes)

        assert nbytes > 0

        if signed is None:
            signed = cls.__signed__

        signed = bool(signed)

        if byteorder is None:
            byteorder = cls.__byteorder__

        assert byteorder in {'big', 'little'}

        if dref is None:
            dref = cls.__dref__

        if dref is not None:
            assert isinstance(dref, PlumType), f"{dref!r} must be a {PlumType!r} instance"

        if signed:
            minvalue = -(1 << (nbytes * 8 - 1))
            maxvalue = (1 << (nbytes * 8 - 1)) - 1
        else:
            minvalue = 0
            maxvalue = (1 << (nbytes * 8)) - 1

        # store byteorder, nbytes, signed separately for use later
        # to pack/unpack to be able to support any sized integer
        # (versus storing struct pack/unpack function similar to
        # float type which is restricted to common sizes).

        cls.__byteorder__ = byteorder
        cls.__dref__ = dref
        cls.__max__ = maxvalue
        cls.__min__ = minvalue
        cls.__nbytes__ = nbytes
        cls.__signed__ = signed

        try:
            boostable = namespace['__boostable__']
        except KeyError:
            if '__pack__' in namespace or '__unpack__' in namespace:
                cls.__boostable__ = False
            boostable = cls.__boostable__

        if boost and boostable:  # pragma: no cover
            # attach binary string containing plum-c accelerator "C" structure
            # (so structure memory de-allocated when class deleted)
            cls.__plum_boost_internals__ = boost.fastint.add_c_acceleration(
                cls, nbytes, byteorder == 'little', signed,
                type(cls).__unpack_int__, cls.__strict_enum__)

            cls.__pack__ = boost.pack_classmethod(cls.__pack__.__func__)
            cls.__unpack__ = boost.unpack_classmethod(cls.__unpack__.__func__)
