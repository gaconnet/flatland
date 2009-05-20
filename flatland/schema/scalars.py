# -*- coding: utf-8; fill-column: 78 -*-
# TODO: Temporal stripping
import datetime
import re

from flatland import valid
from flatland.exc import AdaptationError
from flatland.util import Unspecified, as_mapping, lazy_property
from .base import FieldSchema, Element


__all__ = (
    'Boolean',
    'Date',
    'DateTime',
    'Enum',
    'Float',
    'Integer',
    'Long',
    'Ref',
    'String',
    'Time',
    )


class ScalarElement(Element):
    flattenable = True

    def __init__(self, schema, **kw):
        value = kw.pop('value', Unspecified)

        Element.__init__(self, schema, **kw)

        if value is not Unspecified:
            self.set(value)

    def set(self, value):
        """Assign the native and Unicode value.

        Attempts to adapt the given value and assigns this element's `.value`
        and `.u` attributes in tandem.  Returns True if the adaptation was
        successful.

        If adaptation succeeds, `.value` will contain the adapted native value
        and `.u` will contain a Unicode serialized version of it. A native
        value of None will be represented as u'' in `.u`.

        If adaptation fails, `.value` will be None and `.u` will contain
        `unicode(value)` or u'' for none.

        """
        try:
            # adapt and normalize the value, if possible
            value = self.value = self.schema.adapt(self, value)
        except AdaptationError:
            self.value = None
            if value is None:
                self.u = u''
            elif isinstance(value, unicode):
                self.u = value
            else:
                try:
                    self.u = unicode(value)
                except UnicodeDecodeError:
                    self.u = unicode(value, errors='replace')
            return False

        # stringify it, possibly storing what we received verbatim or a
        # normalized version of it.
        if value is None:
            self.u = u''
        else:
            self.u = self.schema.serialize(self, value)
        return True

    def _index(self, name):
        raise IndexError(name)

    def _set_flat(self, pairs, sep):
        for key, value in pairs:
            if key == self.name:
                self.set(value)
                break

    def set_default(self):
        default = self.default
        if self.default is not Unspecified:
            self.set(default)

    def __nonzero__(self):
        return True if self.u and self.value else False

    def __unicode__(self):
        return self.u

    def __repr__(self):
        return '<%s %r; value=%r>' % (
            type(self.schema).__name__, self.name, self.value)


class Scalar(FieldSchema):
    """The most common type, a single value such as a string or number.

    Scalar subclasses are responsible for translating most data types in and
    out of Python native form: strings, numbers, dates, times, Boolean values,
    etc.  Any data which is represented by a single key, value pair is a
    likely Scalar.

    Scalar subclasses have two responsibilities: provide a method to adapt a
    value to native Python form, and provide a method to serialize the native
    form to a Unicode string.

    Elements can be equality compared (==) to their Unicode representation,
    their native representation or other elements.

    """

    element_type = ScalarElement

    def adapt(self, element, value):
        """Given any value, try to coerce it into native format.

        Returns the native format or raises AdaptationError on failure.

        """
        raise NotImplementedError()

    def serialize(self, element, value):
        """Given any value, coerce it into a Unicode representation.

        No special effort is made to coerce values not of native or a
        compatible type.

        *Must* return a Unicode object, always.

        """
        return unicode(value)

    def validate_element(self, element, state, descending):
        """Validates on the first, downward pass.

        See :meth:`FieldSchema.validate_element`.

        """
        if descending:
            return FieldSchema.validate_element(
                self, element, state, descending)
        else:
            return None


class StringElement(ScalarElement):
    """An Element type with string specific behavior."""

    @property
    def is_empty(self):
        """True if the string is blank or has no value."""
        return True if (not self.value and self.u == u'') else False


class String(Scalar):
    """A regular old Unicode string.

    :arg name: field name
    :arg strip: if ``True``, strip leading and trailing whitespace during
                normalization.

    """

    element_type = StringElement

    def __init__(self, name, strip=True, **kw):
        super(String, self).__init__(name, **kw)
        self.strip = strip

    def adapt(self, element, value):
        """Return a Unicode representation.

        If ``strip=True``, leading and trailing whitespace will be removed.

        :returns: ``unicode(value)`` or ``None``

        """
        if value is None:
            return None
        elif self.strip:
            return unicode(value).strip()
        else:
            return unicode(value)

    def serialize(self, element, value):
        """Return a Unicode representation.

        If ``strip=True``, leading and trailing whitespace will be removed.

        :returns: ``unicode(value)`` or ``u'' if value == None``

        """
        if value is None:
            return u''
        elif self.strip:
            return unicode(value).strip()
        else:
            return unicode(value)


class Number(Scalar):
    """Base for numeric fields.

    :arg name: field name
    :arg signed: if ``False``, disallow negative numbers
    :arg format: override the class's default serialization format

    Subclasses provide :attr:`type_` and :attr:`format` attributes for
    :meth:`adapt` and :meth:`serialize`.

    """

    type_ = None
    format = u'%s'

    def __init__(self, name, signed=True, format=Unspecified, **kw):
        super(Number, self).__init__(name, **kw)
        self.signed = signed
        if format is not Unspecified:
            assert isinstance(format, unicode)
            self.format = format

    def adapt(self, element, value):
        """Generic numeric coercion.

        Attempt to convert *value* using the class's :attr:`type_` callable.

        """
        if value is None:
            return None
        try:
            native = self.type_(value)
        except (ValueError, TypeError):
            raise AdaptationError()
        else:
            if not self.signed:
                if native < 0:
                    raise AdaptationError()
            return native

    def serialize(self, element, value):
        """Generic numeric serialization.

        Converts *value* to a string using Python's string formatting function
        and the :attr:`format` as the template.  The *value* is provided to
        the format as a single, positional format argument.

        """
        if type(value) is self.type_:
            return self.format % value
        return unicode(value)


class Integer(Number):
    """Field type for Python's int."""

    type_ = int
    format = u'%i'


class Long(Number):
    """Field type for Python's long."""

    type_ = long
    format = u'%i'


class Float(Number):
    """Field type for Python's float."""

    type_ = float
    format = u'%f'


# TODO: Decimal

class Boolean(Scalar):
    """Field type for Python's bool.

    :arg name: field name
    :arg true: The Unicode serialization for True
    :arg false: The Unicode serialization for False

    """

    true_synonyms = (u'on', u'true', u'True', u'1')
    false_synonyms = (u'off', u'false', u'False', u'0', u'')

    def __init__(self, name, true=u'1', false=u'', **kw):
        super(Scalar, self).__init__(name, **kw)
        assert isinstance(true, unicode)
        assert isinstance(false, unicode)

        self.true = true
        self.false = false

    def adapt(self, element, value):
        """Coerce value to bool.

        If value is a string, returns True if the value is in
        :attr:`true_synonyms`, False if in :attr:`false_synonyms` and None
        otherwise.

        For non-string values, equivalent to ``bool(value)``.

        """
        if not isinstance(value, basestring):
            return bool(value)
        if value == self.true or value in self.true_synonyms:
            return True
        if value == self.false or value in self.false_synonyms:
            return False
        return None

    def serialize(self, element, value):
        """Convert bool(value) to a canonical string representation.

        Will return either :attr:`self.true` or :attr:`self.false`.

        """
        return self.true if value else self.false


class Constrained(Scalar):
    """A scalar type with a constrained set of legal values.

    Wraps another scalar type and ensures that a value
    :meth:`~flatland.schema.base.Element.set` is within bounds defined by
    :meth:`valid_value`.  If :meth:`valid_value` returns false, the element is
    not converted and will have a :attr:`~flatland.schema.base.Element.value`
    of None.

    :class:`Constrained` is a semi-abstract class that requires an
    implementation of :meth:`valid_value`, either by subclassing or overriding
    on a per-instance basis through the constructor.

    An example of a wrapper of int values that only allows the values of 1, 2
    or 3:

      >>> from flatland.schema import Constrained, Integer
      >>> def is_valid(element, value):
      ...     return value in (1, 2, 3)
      ...
      >>> schema = Constrained('digit', Integer, valid_value=is_valid)
      >>> element = schema.create_element()
      >>> element.set(u'2')
      True
      >>> element.value
      2
      >>> element.set(u'5')
      False
      >>> element.value
      None

    :class:`Enum` is a subclass which provides a convenient enumerated
    wrapper.

    """

    child_type = String

    def __init__(self, name, child_type=None, **kw):
        if child_type:
            self.child_type = child_type
        if 'valid_value' in kw:
            self.valid_value = kw.pop('valid_value')
        Scalar.__init__(self, name, **kw)
        self.child_schema = child = self.child_type(name)
        self.element_type = child.element_type

    def valid_value(self, element, value):
        """Returns True if *value* for *element* is within the constraints.

        This method is abstract.  Override in a subclass or pass a custom
        callable to the :class:`Constrained` constructor.

        """
        return False

    def adapt(self, element, value):
        value = self.child_schema.adapt(element, value)
        if not self.valid_value(element, value):
            raise AdaptationError()
        return value

    def serialize(self, element, value):
        return self.child_schema.serialize(element, value)


class Enum(Constrained):
    """A scalar type with a limited set of valid values."""

    valid_values = ()

    def __init__(self, name, *values, **kw):
        """Create a new Enum.

        :param name: field name

        :param \*values: valid element values.

        :param valid_values: optional, a sequence or other
          containment-supporting collection of valid values.

        :param child_type: defaults to :class:`String`.  Any scalar
          :class:`~flatland.schema.FieldSchema` class for elements of this
          Enum.

        """
        if 'valid_values' in kw:
            assert not values
            self.valid_values = kw.pop('valid_values')
        Constrained.__init__(self, name, **kw)
        if values:
            self.valid_values = values

    def valid_value(self, element, value):
        """True if *value* is within the enumerated values.

        Checks for membership in ``element.valid_values``, if available,
        otherwise falls back to the schema's ``valid_values``.

        """
        valid_values = getattr(element, 'valid_values', self.valid_values)
        return value in valid_values


class Temporal(Scalar):
    """Base for datetime-based date and time fields."""

    type_ = None
    regex = None
    format = None
    used = None

    def __init__(self, name, strip=True, **kw):
        Scalar.__init__(self, name, **kw)
        self.strip = strip

    def adapt(self, element, value):
        """Coerces value to a native type.

        If *value* is an instance of :attr:`type_`, returns it unchanged.  If
        a string, attempts to parse it and construct a :attr:`type` as
        described in the attribute documentation.

        """
        if isinstance(value, self.type_):
            return value
        elif isinstance(value, basestring):
            if self.strip:
                value = value.strip()
            match = self.regex.match(value)
            if not match:
                raise AdaptationError()
            try:
                args = [int(match.group(f)) for f in self.used]
                return self.type_(*args)
            except (TypeError, ValueError), ex:
                raise AdaptationError()
        else:
            raise AdaptationError()

    def serialize(self, element, value):
        """Serializes value to string.

        If *value* is an instance of :attr:`type`, formats it as described in
        the attribute documentation.  Otherwise returns ``unicode(value)``.

        """
        if isinstance(value, self.type_):
            return self.format % as_mapping(value)
        else:
            return unicode(value)


class DateTime(Temporal):
    """Field type for Python datetime.datetime.

    Serializes to and from YYYY-MM-DD HH:MM:SS format.

    """

    type_ = datetime.datetime
    regex = re.compile(
        ur'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) '
        ur'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})$')
    format = (u'%(year)04i-%(month)02i-%(day)02i '
              u'%(hour)02i:%(minute)02i:%(second)02i')
    used = ('year', 'month', 'day', 'hour', 'minute', 'second')


class Date(Temporal):
    """Field type for Python datetime.date.

    Serializes to and from YYYY-MM-DD format.

    """

    type_ = datetime.date
    regex = re.compile(
        ur'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$')
    format = u'%(year)04i-%(month)02i-%(day)02i'
    used = ('year', 'month', 'day')


class Time(Temporal):
    """Field type for Python datetime.time.

    Serializes to and from HH:MM:SS format.

    """

    type_ = datetime.time
    regex = re.compile(
        ur'^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})$')
    format = u'%(hour)02i:%(minute)02i:%(second)02i'
    used = ('hour', 'minute', 'second')


class RefElement(ScalarElement):
    flattenable = False

    @lazy_property
    def target(self):
        return self.root.el(self.schema.path)

    def _get_u(self):
        """The Unicode representation of the reference target."""
        return self.target.u

    def _set_u(self, ustr):
        if self.schema.writable == 'ignore':
            return
        elif self.schema.writable:
            self.target.u = ustr
        else:
            raise TypeError(u'Ref "%s" is not writable.' % self.name)

    u = property(_get_u, _set_u)
    del _get_u, _set_u

    def _get_value(self):
        """The native value representation of the reference target."""
        return self.target.value

    def _set_value(self, value):
        if self.schema.writable == 'ignore':
            return
        elif self.schema.writable:
            self.target.value = value
        else:
            raise TypeError(u'Ref "%s" is not writable.' % self.name)

    value = property(_get_value, _set_value)
    del _get_value, _set_value


class Ref(Scalar):
    """A functional reference to another element."""

    element_type = RefElement

    def __init__(self, name, path, writable='ignore', sep='.', **kw):
        super(Ref, self).__init__(name, **kw)

        self.path = list(self.element_type._parse_element_path(path, sep))
        assert self.path is not None

        self.writable = writable

    def adapt(self, element, value):
        return element.target.schema.adapt(element, value)

    def serialize(self, element, value):
        return element.target.schema.serialize(element, value)
