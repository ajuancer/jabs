# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Test utilities."""

from textwrap import wrap


def wrap_message(exc):
    """Line wrap exception message.

     Wrap exception message lines that exceed 80 characters.
     Detect and leave undisturbed `dump()` tables.

     :param Exception exc: exception
     :returns: wrapped exception message
     :rtype: str

     """
    lines_out = []
    queue = []
    for line in str(exc).split('\n'):
        stripped_line = line.strip()
        if not stripped_line or (stripped_line[0] in '+|'):
            lines_out.extend(wrap('\n'.join(queue)))
            lines_out.append(line)
            queue = []
        else:
            queue.append(line)

    if queue:  # pragma: no cover
        lines_out.extend(wrap('\n'.join(queue)))

    return '\n'.join(lines_out)
