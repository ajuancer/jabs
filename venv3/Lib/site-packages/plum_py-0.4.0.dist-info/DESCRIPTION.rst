
#########################
[plum] Pack/Unpack Memory
#########################

.. image:: https://readthedocs.org/projects/plum-py/badge/?version=latest
    :target: https://plum-py.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


The ``plum-py`` Python package provides classes and utility functions to
efficiently pack and unpack bytes similar to what the standard library
``struct`` module offers. This package expands significantly on that 
capability with much more powerful and convenient access and control of 
bytes within a buffer (including handling variable size/type 
relationships within the buffer data).

The package provides a large number of fundamental types (e.g. numbers, 
structures, arrays, etc.) for specifying buffer data structure. Each 
type conforms to a "plug-and-play" architecture facilitating the ability 
to be combined in any way, including deeply nested structures of arbitrary 
type. You may also write your own custom types that conform to the 
"plug-and-play" architecture API and use them in combination with any of 
the fundamental types provided.

