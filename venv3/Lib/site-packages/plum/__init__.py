# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Classes and utilities for packing/unpacking bytes."""

import os

from ._buffer import Buffer
from ._exceptions import (
    ExcessMemoryError,
    ImplementationError,
    InsufficientMemoryError,
    PackError,
    SizeError,
    UnpackError,
)

from ._plum import (
    Plum,
    getbytes,
    pack,
    pack_and_dump,
    pack_into,
    pack_into_and_dump,
    plum_namespace,
    unpack,
    unpack_and_dump,
    unpack_from,
    unpack_from_and_dump,
)
from ._plumview import PlumView
from ._plumtype import PlumType


enable_boost = os.environ.get('ENABLE_PLUM_BOOST', 'AUTO').upper()

if enable_boost in {'AUTO', 'YES'}:  # pragma: no cover
    try:
        import plum_boost as boost  # pylint: disable=import-error
    except ModuleNotFoundError:
        if enable_boost == 'YES':
            raise
        boost = None
    else:
        pack = plum_namespace['pack'] = boost.pack
        unpack = plum_namespace['unpack'] = boost.unpack
        unpack_from = plum_namespace['unpack_from'] = boost.unpack_from
        Plum.pack = boost.PackMethod()
        Plum.unpack = classmethod(boost.unpack)

elif enable_boost == 'NO':  # pragma: no cover
    boost = None

else:  # pragma: no cover
    raise RuntimeError('ENABLE_PLUM_BOOST environment variable must be YES, NO, or AUTO')

del enable_boost, os, plum_namespace
