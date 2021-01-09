# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Plum type conformance test base classes."""

import logging
from io import BytesIO

import pytest

from plum import (
    Buffer,
    ExcessMemoryError,
    InsufficientMemoryError,
    SizeError,
    UnpackError,
    pack,
    pack_and_dump,
    pack_into,
    pack_into_and_dump,
    unpack,
    unpack_from,
    unpack_and_dump,
    unpack_from_and_dump,
)

from ._utils import wrap_message

# pylint: disable=unidiomatic-typecheck


class SampleType(type):

    """Sample class metaclass."""

    def __new__(mcs, name, bases, namespace, validate=True):
        # pylint: disable=unused-argument
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, validate=True):
        super().__init__(name, bases, namespace)

        if validate:
            basecls = cls.__basecls__

            base_dir = {n for n in dir(basecls) if not n.startswith('_')}

            for methname in {n for n in base_dir if not n.startswith('test')}:
                # pylint: disable=line-too-long
                if (getattr(basecls, methname) is ...) and (getattr(cls, methname) is ...):  # pragma: no cover
                    raise TypeError(f'subclass missing {methname!r} attribute')

            cls_dir = {n for n in dir(cls) if not n.startswith('_')}

            extras = {n for n in cls_dir - base_dir if not n.startswith('test')}

            if extras:  # pragma: no cover
                extras = list(sorted(extras))
                raise TypeError(f'illegal subclass attribute {extras}')
        else:
            # subclasses validate attributes against me
            cls.__basecls__ = cls


class Sample(metaclass=SampleType, validate=False):

    """Conformance test attributes."""

    __basecls__ = None

    plumtype = ...
    """Plum type to test."""

    unpack_cls = None

    value = ...
    """Sample value to use to construct plum type instance and to compare."""

    def iter_instances(self):
        """Iterate sample instances.

        :returns: sample instance, description
        :rtype: object, str

        """
        yield self.plumtype(self.value), "instantiated from self.value"

    def iter_values(self):
        """Iterate sample equivalent values.

        :returns: sample value, description
        :rtype: object, str

        """
        yield self.value, "sample built-in value"
        yield self.plumtype(self.value), "sample plum type instance"


class BasicConformance(Sample, validate=False):  # pylint: disable=too-many-public-methods

    """Test basic API conformance and utility usage."""

    bindata = ...
    """Sample packed binary data."""

    cls_nbytes = None
    """Size of plum type being tested."""

    dump = ...
    """Expected dump of sample plum type instance."""

    greedy = False
    """If plum type being tested consumes remaining bytes."""

    retval_str = ...
    """Expected return value of __str__ method."""

    retval_repr = ...
    """Expected return value of __repr__ method."""

    unpack_excess = ...
    """Expected exception message of unpack() method when 1 byte extra."""

    unpack_shortage = ...
    """Expected exception message of unpack() method when short 1 byte."""

    def test_init(self):
        """Test instantiation of sample instances."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            assert instance.dump == self.dump

    def test_nbytes_property_with_cls(self):
        """Test nbytes property with plum type."""
        if self.cls_nbytes is None:
            with pytest.raises(SizeError):
                # pylint: disable=pointless-statement
                self.plumtype.nbytes
        else:
            assert self.plumtype.nbytes == self.cls_nbytes

    def test_nbytes_property_with_instance(self):
        """Test nbytes property with plum type instance."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            assert instance.nbytes == len(self.bindata)

    def test_dump(self):
        """Test dump property usage."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            assert instance.dump == self.dump

    def test_pack_value(self):
        """Test pack passing built in type (and equivalents) as value."""
        for value, desc in self.iter_values():
            logging.info(desc)
            # utility function
            assert pack(self.plumtype, value) == self.bindata
            # class method
            assert self.plumtype.pack(value) == self.bindata

    def test_pack_instance(self):
        """Test pack passing sample instance as value."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            # utility function
            assert pack(self.plumtype, instance) == self.bindata
            # instance method
            assert instance.pack() == self.bindata
            # class method
            assert self.plumtype.pack(instance) == self.bindata

    def test_pack_and_dump_value(self):
        """Test pack_and_dump() passing built in type (and equivalents) as value."""
        for value, desc in self.iter_values():
            logging.info(desc)
            # utility function
            buffer, dump = pack_and_dump(self.plumtype, value)
            assert buffer == self.bindata
            assert dump == self.dump
            # class method
            buffer, dump = self.plumtype.pack_and_dump(value)
            assert buffer == self.bindata
            assert dump == self.dump

    def test_pack_and_dump_instance(self):
        """Test pack_and_dump() passing sample instance as value."""
        for instance, desc in self.iter_instances():
            logging.info(desc)

            # utility function
            buffer, dump = pack_and_dump(self.plumtype, instance)
            assert buffer == self.bindata
            assert dump == self.dump

            # instance method
            buffer, dump = instance.pack_and_dump()
            assert buffer == self.bindata
            assert dump == self.dump

            # class method
            buffer, dump = self.plumtype.pack_and_dump(instance)
            assert buffer == self.bindata
            assert dump == self.dump

    def test_pack_into_value(self):
        """Test pack_into() passing sample values."""
        for value, desc in self.iter_values():
            logging.info(desc)

            # utility function
            buffer = bytearray()
            pack_into(self.plumtype, buffer, 0, value)
            assert buffer == self.bindata

            # class method
            buffer = bytearray()
            self.plumtype.pack_into(buffer, 0, value)
            assert buffer == self.bindata

    def test_pack_into_instance(self):
        """Test pack_into() passing sample instance as value."""
        for instance, desc in self.iter_instances():
            logging.info(desc)

            # utility function
            buffer = bytearray()
            pack_into(self.plumtype, buffer, 0, instance)
            assert buffer == self.bindata

            # instance method
            buffer = bytearray()
            instance.pack_into(buffer, 0)
            assert buffer == self.bindata

            # class method
            buffer = bytearray()
            self.plumtype.pack_into(buffer, 0, instance)
            assert buffer == self.bindata

    def test_pack_into_and_dump_value(self):
        """Test pack_into_and_dump() passing sample value."""
        for value, desc in self.iter_values():
            logging.info(desc)

            # utility function
            buffer = bytearray()
            dump = pack_into_and_dump(self.plumtype, buffer, 0, value)
            assert buffer == self.bindata
            assert dump == self.dump

            # class method
            buffer = bytearray()
            dump = self.plumtype.pack_into_and_dump(buffer, 0, value)
            assert buffer == self.bindata
            assert dump == self.dump

    def test_pack_into_and_dump_instance(self):
        """Test pack_into_and_dump() passing sample instance as value."""
        for instance, desc in self.iter_instances():
            logging.info(desc)

            # utility function
            buffer = bytearray()
            dump = pack_into_and_dump(self.plumtype, buffer, 0, instance)
            assert buffer == self.bindata
            assert dump == self.dump

            # instance method
            buffer = bytearray()
            dump = instance.pack_into_and_dump(buffer, 0)
            assert buffer == self.bindata
            assert dump == self.dump

            # class method
            buffer = bytearray()
            dump = self.plumtype.pack_into_and_dump(buffer, 0, instance)
            assert buffer == self.bindata
            assert dump == self.dump

    def test_unpack(self):
        """Test unpack()."""
        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item = unpack(self.plumtype, self.bindata)
        assert type(item) is expected_cls
        assert item == self.value

        # class method
        item = self.plumtype.unpack(self.bindata)
        assert type(item) is expected_cls
        assert item == self.value

        # bytes Buffer
        with Buffer(self.bindata) as buffer:
            item = buffer.unpack(self.plumtype)
        assert type(item) is expected_cls
        assert item == self.value

    def test_unpack_from_default_start(self):
        """Test unpack_from() usage with offset at start.

        Unpack from start of buffer and where offset is not specified
        in call.

        """
        if self.greedy:
            buffer = self.bindata
        else:
            buffer = self.bindata + b'\x99'

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item = unpack_from(self.plumtype, buffer)
        assert type(item) is expected_cls
        assert item == self.value

        # class method
        item = self.plumtype.unpack_from(buffer)
        assert type(item) is expected_cls
        assert item == self.value

    def test_unpack_from_default_middle(self):
        """Test unpack_from() usage with offset in middle.

        Unpack from middle of buffer and where offset is not specified
        in call (BytesIO instance has already been read).

        """
        if self.greedy:
            buffer = BytesIO(b'\x99' + self.bindata)
        else:
            buffer = BytesIO(b'\x99' + self.bindata + b'\x99')

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        buffer.seek(1)
        item = unpack_from(self.plumtype, buffer)
        assert type(item) is expected_cls
        assert item == self.value

        # class method
        buffer.seek(1)
        item = self.plumtype.unpack_from(buffer)
        assert type(item) is expected_cls
        assert item == self.value

    def test_unpack_from_force_middle(self):
        """Test unpack_from() usage with offset pointing to middle.

        Unpack from middle of buffer and where offset is specified in call.

        """
        if self.greedy:
            buffer = b'\x99' + self.bindata
        else:
            buffer = b'\x99' + self.bindata + b'\x99'

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item = unpack_from(self.plumtype, buffer, offset=1)
        assert type(item) is expected_cls
        assert item == self.value

        # class method
        item = self.plumtype.unpack_from(buffer, offset=1)
        assert type(item) is expected_cls
        assert item == self.value

    def test_unpack_and_dump(self):
        """Test unpack_and_dump()."""
        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item, dump = unpack_and_dump(self.plumtype, self.bindata)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump == self.dump

        # class method
        item, dump = self.plumtype.unpack_and_dump(self.bindata)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump == self.dump

        # bytes Buffer
        with Buffer(self.bindata) as buffer:
            item, dump = buffer.unpack_and_dump(self.plumtype)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump == self.dump

    def test_unpack_from_and_dump_default_start(self):
        """Test unpack_from_and_dump() usage with offset at start.

        Unpack from start of buffer and where offset is not specified
        in call.

        """
        if self.greedy:
            buffer = self.bindata
        else:
            buffer = self.bindata + b'\x99'

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item, dump = unpack_from_and_dump(self.plumtype, buffer)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump == self.dump

        # class method
        item, dump = self.plumtype.unpack_from_and_dump(buffer)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump == self.dump

    def test_unpack_from_and_dump_default_middle(self):
        """Test unpack_from_and_dump() usage with offset in middle.

        Unpack from middle of buffer and where offset is not specified
        in call (BytesIO instance has already been read).

        """
        if self.greedy:
            buffer = BytesIO(b'\x99' + self.bindata)
        else:
            buffer = BytesIO(b'\x99' + self.bindata + b'\x99')

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        buffer.seek(1)
        item, dump = unpack_from_and_dump(self.plumtype, buffer)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump.offset == 1
        dump.offset = 0  # normalize dump (for compare against baseline)
        assert dump == self.dump

        # class method
        buffer.seek(1)
        item, dump = self.plumtype.unpack_from_and_dump(buffer)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump.offset == 1
        dump.offset = 0  # normalize dump (for compare against baseline)
        assert dump == self.dump

    def test_unpack_from_and_dump_force_middle(self):
        """Test unpack_from_and_dump() usage with offset pointing to middle.

        Unpack from middle of buffer and where offset is specified in call.

        """
        if self.greedy:
            buffer = b'\x99' + self.bindata
        else:
            buffer = b'\x99' + self.bindata + b'\x99'

        expected_cls = self.unpack_cls or self.plumtype

        # utility function
        item, dump = unpack_from_and_dump(self.plumtype, buffer, offset=1)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump.offset == 1
        dump.offset = 0
        assert dump == self.dump

        # class method
        item, dump = self.plumtype.unpack_from_and_dump(buffer, offset=1)
        assert type(item) is expected_cls
        assert item == self.value
        assert dump.offset == 1
        dump.offset = 0
        assert dump == self.dump

    def test_unpack_shortage(self):
        """Test unpack() usage with insufficient bytes."""
        if str(self.unpack_shortage) != 'N/A':  # str() isolates from baseline behavior
            if self.bindata:  # pragma: no cover
                with pytest.raises(UnpackError) as trap:
                    unpack(self.plumtype, self.bindata[:-1])

                assert wrap_message(trap.value) == self.unpack_shortage
                assert isinstance(trap.value.__context__, InsufficientMemoryError)

    def test_unpack_excess(self):
        """Test unpack() usage with excess bytes."""
        if str(self.unpack_excess) != 'N/A':  # str() isolates from baseline behavior
            with pytest.raises(UnpackError) as trap:
                unpack(self.plumtype, self.bindata + b'\x99')

            assert wrap_message(trap.value) == self.unpack_excess
            assert isinstance(trap.value.__context__, ExcessMemoryError)

    def test_str(self):
        """Test plum type instance __str__ support."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            assert str(instance) == self.retval_str

    def test_repr(self):
        """Test plum type instance __repr__ support."""
        for instance, desc in self.iter_instances():
            logging.info(desc)
            assert repr(instance) == self.retval_repr
