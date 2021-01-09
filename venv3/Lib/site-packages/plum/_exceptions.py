# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Exception classes related to packing/unpacking bytes."""


class UnpackError(Exception):

    """Unpack error."""


class ExcessMemoryError(UnpackError):

    """Leftover bytes after unpack operation."""

    def __init__(self, message, extra_bytes):
        super(ExcessMemoryError, self).__init__(message, extra_bytes)
        self.extra_bytes = extra_bytes

    def __str__(self):
        # pylint: disable=unsubscriptable-object
        return self.args[0]


class ImplementationError(Exception):

    """Unexpected implementation error."""

    def __init__(self, message=''):
        if not message:
            message = (
                'One of the plum types used in the pack/unpack operation '
                'contains an implementation error. The operation generated '
                'an exception when first performed without a dump (for efficiency). '
                'But when the operation was repeated with a dump (for a better '
                'exception message) the exception did not re-occur. Please report '
                'the inconsistent behavior to the type developer.'
            )
        super(ImplementationError, self).__init__(message)


class InsufficientMemoryError(UnpackError):

    """Too few bytes to unpack an item."""


class PackError(Exception):

    """Pack operation error."""


class SizeError(Exception):

    """Size varies from instance to instance."""
