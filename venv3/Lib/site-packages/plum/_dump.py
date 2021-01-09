# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Pack/unpack bytes summary."""


class Record(list):

    """Pack/unpack bytes summary.

    :param bool separate: add separator before row
    :param str access: access description
    :param str value: representation of value associated with bytes
    :param bits: start, end bit offset (None -> not a bit field)
    :type bits: tuple of (int, int)
    :param bytes memory: bytes
    :param str cls: plumtype name
    :param list rows: summary rows
    :param int offset: master byte offset

    """

    def __init__(self, access='', value='', bits=None, memory=b'', cls='', separate=False):
        # pylint: disable=too-many-arguments
        super(Record, self).__init__()
        self.access = access
        self._value = value
        self._bits = bits
        self.memory = memory
        self.cls = cls
        self.separate = separate

    def __bool__(self):
        return True

    def add_record(self, access='', value='', bits=None, memory=b'', cls='', separate=False):
        """Add child record.

        :param str access: access description
        :param str value: value representation associated with bytes
        :param bits: start, end bit offset (None -> not a bit field)
        :type bits: tuple of (int, int)
        :param bytes memory: bytes
        :param str cls: plumtype name
        :param bool separate: add separator before row

        """
        # pylint: disable=too-many-arguments
        record = Record(access, value, bits, memory, cls, separate)
        self.append(record)
        return record

    def add_extra_bytes(self, access, memory):
        """Add records listing bytes without access/value descriptions.

        :param str access: access description
        :param bytes memory: extra bytes

        """
        for i in range(0, len(memory), 16):
            self.add_record(access=access, memory=memory[i:i + 16])
            access = ''

    def iter_records(self, indent=0):
        """Iterate dump records.

        :returns: generator yielding records
        :rtype: generator

        """
        yield indent, self
        for record in self:
            yield from record.iter_records(indent + 1)

    @property
    def bits(self):
        """Bit field representation.

        :returns: representation, e.g. ``[0:3]``
        :rtype: str

        """
        try:
            pos, size = self._bits
        except TypeError:
            # bits is None
            bits = ''
        else:
            end = pos + size - 1
            if end == pos:
                bits = f'[{pos}]'
            else:
                bits = f'[{pos}:{pos + size - 1}]'
        return bits

    @property
    def value(self):
        """Value representation.

        :returns: representation
        :rtype: str

        """
        return str(self._value)

    @value.setter
    def value(self, value):
        """Value representation.

        :param object value: new value

        """
        self._value = value

    @property
    def bytes(self):
        """Memory bytes hexidecimal list.

        :returns: list summary, e.g. ``"00 12 34 56 78 9A BC CD EF"``
        :rtype: str

        """
        return ' '.join('{:02x}'.format(c) for c in self.memory)

    @property
    def type(self):
        """Representation of type.

        :returns: representation
        :rtype: str

        """
        return self.cls.__name__ if isinstance(self.cls, type) else str(self.cls)


class Dump(list):

    """Pack/unpack bytes summary.

    :param int offset: master byte offset

    """

    def __init__(self, offset=0):
        super(Dump, self).__init__()
        self.offset = offset

    def __call__(self):
        print(self)

    # borrow method implementations
    add_record = Record.add_record
    add_extra_bytes = Record.add_extra_bytes
    __bool__ = Record.__bool__

    def iter_records(self):
        """Iterate dump records.

        :returns: generator yielding records
        :rtype: generator

        """
        for record in self:
            yield from record.iter_records()

    def _get_offset_column_cells(self, records):
        bits = [record.bits for record in records]

        # make bit offset information uniform in length
        if any(bits):
            fmt = '{:%ds}' % max(len(bits_desc) for bits_desc in bits)
            bits = [fmt.format(bits_desc) for bits_desc in bits]

        # compute offset cells (with bit descriptions appended on)
        nbytes = sum(len(record.memory) for record in records)
        offset_template = '{:%dd}' % len(str(nbytes + self.offset))
        filler = ' ' * len(str(nbytes))
        consumed = 0
        offsets = []
        for record, bits_desc in zip(records, bits):
            if record.memory:
                byte_offset = offset_template.format(self.offset + consumed)
                consumed += len(record.memory)
            else:
                byte_offset = filler
            offsets.append(byte_offset + bits_desc)

        return offsets

    def _get_lines(self):
        if len(self):  # pylint: disable=len-as-condition
            indents, records = zip(*self.iter_records())
        else:
            indents, records = [0], [Record()]

        accesses = [record.access.replace('(.)', '') for record in records]

        # look for things like this and get rid of excess indentation
        # +--------+-------------+-----------+-------+-----------------+
        # | Offset | Access      | Value     | Bytes | Type            |
        # +--------+-------------+-----------+-------+-----------------+
        # |        |             |           |       | CustomStructure |
        # | 0      |   [0] (.m1) | 258       | 02 01 | UInt16          |
        # | 2      |   [1] (.m2) | <invalid> | 00    | CustomError     |
        # +--------+-------------+-----------+-------+-----------------+
        if all(indent or not access for indent, access in zip(indents, accesses)):
            indents = [indent - 1 if indent else 0 for indent in indents]

        columns = [
            ['Offset'] + self._get_offset_column_cells(records),
            # 'Access' gets inserted here
            ['Value'] + [record.value for record in records],
            ['Bytes'] + [record.bytes for record in records],
            ['Type'] + [record.type for record in records],
        ]

        if any(accesses):
            columns[1:1] = [
                ['Access'] +
                ['  ' * indent + access for indent, access in zip(indents, accesses)]]

        column_widths = [max([len(cell) for cell in column]) for column in columns]

        border = '+{}+'.format('+'.join('-' * (n + 2) for n in column_widths))
        row_template = '|{}|'.format('|'.join(' {:%ds} ' % n for n in column_widths))

        rows = list(zip(*columns))
        separators = [record.separate for record in records]
        separators[0] = False

        yield border
        yield row_template.format(*rows.pop(0))  # header names
        yield border
        for cells, separate in zip(rows, separators):
            if separate:
                yield border
            yield row_template.format(*cells)
        yield border

    def __str__(self):
        return '\n'.join(self._get_lines())

    def __eq__(self, other):
        return (other is self) or (other == str(self))

    def __ne__(self, other):
        return not self.__eq__(other)
