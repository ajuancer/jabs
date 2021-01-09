# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2020 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""Structure type metaclass."""

from types import FunctionType, MethodType

from plum import boost
from plum._plumtype import PlumType
from plum.structure._bitfield_member import BitFieldMember
from plum.structure._member import Member


NO_MEMBERS_DEFINED = (), ()


class MemberInfo:

    """Structure member information."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, namespace):
        annotations = namespace.get('__annotations__', {})

        self.bitfields = []
        self.member_definitions = []  # all but BitFieldMember
        self.required_parameter_names = []
        self.optional_parameter_names = []
        self.optional_parameter_defaults = []
        self.internal_parameters = []
        self.member_initializations = []
        self.default_factory_lines = []
        self.sizes = []
        self.members = {
            key: value for key, value in namespace.items() if isinstance(value, Member)}
        self.type_hints = {
            name: annotations.get(name, None) for name in self.members}

        names = [
            name for name, value in namespace.items() if isinstance(value, Member)]

        while names:
            name = names[0]
            member = self.members[name]

            if isinstance(member, BitFieldMember):
                for bitfield_name in self._process_bitfield_members(
                        names, member.cls, namespace):
                    names.remove(bitfield_name)
            else:
                self._process_member(name, member)
                names.remove(name)

        for member in self.member_definitions:
            member.adjust_members(self.members)

        for member in self.member_definitions:
            member.finalize(self.members)

        if self.sizes:
            try:
                self.nbytes = sum(self.sizes)
            except TypeError:
                # has variably sized member (member nbytes is None)
                self.nbytes = None
        else:
            self.nbytes = None

    def __bool__(self):
        return bool(self.member_definitions)

    def _process_bitfield_members(self, names, bitfields_cls, namespace):
        actual_names = set()
        for name in names:
            member = self.members[name]
            if isinstance(member, BitFieldMember) and member.cls is bitfields_cls:
                actual_names.add(name)
            else:
                break

        if actual_names != set(bitfields_cls.__fields__):
            if len(actual_names) != len(bitfields_cls.__fields__):
                raise TypeError(
                    f'{bitfields_cls.__name__!r} bit fields must all be present '
                    f'and in one group')
            raise TypeError(
                f'{bitfields_cls.__name__!r} bit field names must match the following: '
                f'{", ".join(bitfields_cls.__fields__)}')

        bitfields_index = len(self.member_definitions)

        # add actual "hidden" member to implement the fields
        self._process_member('', Member(cls=bitfields_cls))

        for name in bitfields_cls.__fields__:
            member = self.members[name]
            member.finish_initialization(
                bitfields_index, name, self.type_hints)

            default = member.default

            if default is None:
                default = getattr(bitfields_cls, name).default

            if default is None:
                self.required_parameter_names.append(name)
            else:
                self.optional_parameter_names.append(name)
                self.optional_parameter_defaults.append(default)

            namespace[name] = member.get_accessor()

        return actual_names

    def _process_member(self, name, member):
        member_index = len(self.member_definitions)
        member.finish_initialization(member_index, name, self.type_hints)

        self.member_definitions.append(member)

        if name:
            self.member_initializations.append(name)
            if member.default is None:
                self.required_parameter_names.append(name)
            else:
                if isinstance(member.default, (FunctionType, MethodType)):
                    default_index = len(self.optional_parameter_defaults)
                    self.default_factory_lines += [
                        '',
                        f'if {member.name} is None:',
                        f'    self[{member_index}] = _defaults[{default_index}](self)',
                    ]
                self.optional_parameter_names.append(name)
                self.optional_parameter_defaults.append(member.default)
        else:
            # must be a bitfields member where init has args for individual fields
            args = ', '.join(
                f'{name}={name}' for name in member.cls.__fields__)
            self.member_initializations.append(
                f'_{member.cls.__name__}({args})')
            self.internal_parameters.append(
                f'_{member.cls.__name__}=__bitfields__[{len(self.bitfields)}]')
            self.bitfields.append(member.cls)

        self.sizes.append(member.cls.__nbytes__)

    def make_init(self):
        """Construct __init__ method.

        :return: method source code
        :rtype: str

        """
        parameters = list(self.required_parameter_names)

        for index, (name, default) in enumerate(zip(
                self.optional_parameter_names, self.optional_parameter_defaults)):

            if isinstance(default, (FunctionType, MethodType)):
                parameters.append(f'{name}=None')
            else:
                parameters.append(f'{name}=__defaults__[{index}]')

        parameters += self.internal_parameters

        if self.default_factory_lines:
            parameters += ['_defaults=__defaults__']

        lines = [f'def __init__(self, {", ".join(parameters)}):']

        if len(self.member_initializations) == 1:
            lines += [f'list.append(self, {self.member_initializations[0]})']
        else:
            init_values = ', '.join(self.member_initializations)
            lines += [f'list.extend(self, ({init_values}))']

        lines += self.default_factory_lines

        # print('\n    '.join(lines))
        return '\n    '.join(lines)

    @property
    def offsets(self):
        """Member byte offsets relative to the start of the structure.

        For views of structure.

        :returns: byte offsets (or None if variably sized members)
        :rtype: type(None) or list of int

        """
        offsets = []
        cursor = 0

        for member in self.member_definitions:
            offsets.append(cursor)
            try:
                cursor += member.cls.__nbytes__
            except TypeError:
                offsets = None
                break

        return offsets


class StructureType(PlumType):

    """Structure type metaclass.

    Create custom |Structure| subclass. For example:

        >>> from plum.structure import Structure
        >>> from plum.int.little import UInt16, UInt8
        >>> class MyStruct(Structure):
        ...     m0: UInt16
        ...     m1: UInt8
        ...
        >>>

    """

    # the Structure reference is later store here (after its
    # created) so that this metaclass can determine if methods
    # have been overridden so as to not generate them (done
    # this way to avoid circular import)
    structure_class = type(None)

    @classmethod
    def _is_method_overridden(mcs, name, base_class, namespace):
        # determine the underlying function that the base class utilizes
        base_method = getattr(base_class, name)
        try:
            base_method = base_method.__func__
        except AttributeError:
            pass

        # determine the underlying function in the Structure class
        structure_method = getattr(mcs.structure_class, name)

        try:
            structure_method = structure_method.__func__
        except AttributeError:
            pass

        return name in namespace or base_method is not structure_method

    def __new__(mcs, name, bases, namespace):
        # pylint: disable=too-many-locals,too-many-branches
        member_info = MemberInfo(namespace)

        # don't allow members to be redefined ... too complicated otherwise
        for base_class in bases:
            if issubclass(base_class, mcs.structure_class):
                existing_members = base_class.__names_types__ != NO_MEMBERS_DEFINED

                if member_info and existing_members:
                    raise TypeError(
                        f"members already defined by base class "
                        f"{base_class.__name__!r}")

                break
        else:
            # to keep pylint happy - should never get here
            base_class = mcs.structure_class

        if member_info:
            nbytes = member_info.nbytes
            names = tuple(member.name for member in member_info.member_definitions)
            types = tuple(member.cls for member in member_info.member_definitions)

            namespace['__ignore_flags__'] = [
                member.ignore for member in member_info.member_definitions]
            namespace['__nbytes__'] = nbytes
            namespace['__names_types__'] = (names, types)
            namespace["__offsets__"] = member_info.offsets

            # create custom __init__ within class namespace
            if not mcs._is_method_overridden('__init__', base_class, namespace):
                # pylint: disable=exec-used
                namespace['__defaults__'] = tuple(member_info.optional_parameter_defaults)
                namespace['__bitfields__'] = tuple(member_info.bitfields)
                exec(member_info.make_init(), globals(), namespace)
                del namespace['__defaults__']
                del namespace['__bitfields__']

            # install member accessors (in some cases its the same member definition, in
            # other cases member definition returns a custom accessor)
            for member in member_info.member_definitions:
                if member.name:
                    namespace[member.name] = member.get_accessor()

        cls = super().__new__(mcs, name, bases, namespace)

        if boost and cls.__names_types__ != NO_MEMBERS_DEFINED:  # pragma: no cover
            for method_name in ['__pack__', '__unpack__']:
                if mcs._is_method_overridden(method_name, base_class, namespace):
                    break
            else:
                nbytes = cls.__nbytes__
                _names, types = cls.__names_types__

                # attach binary string containing plum-c accelerator "C" structure
                # (so structure memory de-allocated when class deleted)
                cls.__plum_boost_internals__ = boost.faststructure.add_c_acceleration(
                    cls, -1 if nbytes is None else nbytes, len(types), types)

                cls.__pack__ = boost.pack_classmethod(cls.__pack__.__func__)
                cls.__unpack__ = boost.unpack_classmethod(cls.__unpack__.__func__)

        return cls
