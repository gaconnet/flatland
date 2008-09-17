from __future__ import absolute_import

import datetime
import re
import xml.sax.saxutils

from .base import FieldSchema, Element
from flatland.util import (
    Unspecified,
    as_mapping,
    lazy_property,
    )
import flatland.exc as exc


__all__ = ('String', 'Integer', 'Long', 'Float', 'Boolean', 'Date', 'Time',
           'Ref')


# FIXME
unspecified = object()

class _ScalarElement(Element):
    flattenable = True

    def __init__(self, schema, **kw):
        value = kw.pop('value', unspecified)

        Element.__init__(self, schema, **kw)

        if value is not unspecified:
            self.set(value)
        # TODO: wtf does the comment below mean?
        # This prevents sub-types from implementing special sauce
        # for default value of None, but it does make construction
        # faster.
        elif schema.default is not None:
            self.set(schema.default)

    def set(self, value):
        """Assign the native and Unicode value.

        Attempts to adapt the given value and assigns this element's
        `.value` and `.u` attributes in tandem.  Returns True if the
        adaptation was successful.

        If adaptation succeeds, `.value` will contain the adapted
        native value and `.u` will contain a Unicode serialized
        version of it. A native value of None will be represented as
        u'' in `.u`.

        If adaptation fails, `.value` will be None and `.u` will
        contain `unicode(value)` or u'' for none.

        """

        try:
            # adapt and normalize the value, if possible
            value = self.value = self.schema.adapt(self, value)
        except exc.AdaptationError:
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

        # stringify it, possibly storing what we received verbatim or
        # a normalized version of it.
        if value is None:
            self.u = u''
        else:
            self.u = self.schema.serialize(self, value)
        return True

    def _el(self, path):
        if not path:
            return self
        raise KeyError()

    def _set_flat(self, pairs, sep):
        for key, value in pairs:
            if key == self.name:
                self.set(value)
                break

    def __eq__(self, other):
        """
        Overloaded comparison: when comparing elements, compare name
        and value. When comparing non-elements, coerce our value into
        something comparable.
        """

        # ugh
        if isinstance(self, _RefElement) and isinstance(other, Element):
            return self.target is other
        if ((type(self) is type(other)) or isinstance(other, _ScalarElement)):
            if self.name == other.name:
                if self.u == other.u:
                    if self.value == other.value:
                        return True
            return False
        elif isinstance(other, _RefElement):
            if self.path == other.schema.path:
                if self.u == other.u:
                    if self.value == other.value:
                        return True
            return False
        elif isinstance(other, Element):
            return NotImplemented
        else:
            if isinstance(other, basestring):
                if isinstance(self.value, basestring):
                    return self.value == other
                else:
                    return self.u == other
            else:
                return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return True if self.u and self.value else False

    def _validate(self, state=None, validators=None):
        if self.schema.optional and self.u == u'':
            return True
        else:
            return super(_ScalarElement, self)._validate(state, validators)

    def __unicode__(self):
        return self.u

    def __repr__(self):
        return '<%s %r; value=%r>' % (
            type(self.schema).__name__, self.name, self.value)


class Scalar(FieldSchema):
    """The most common type, a single value such as a string or number.

    Scalar subclasses are responsible for translating most data types
    in and out of Python native form: strings, numbers, dates, times,
    Boolean values, etc.  Any data which is represented by a single
    key, value pair is a likely Scalar.

    Scalar subclasses have two responsibilities: provide a method to
    adapt a value to native Python form, and provide a method to
    serialize the native form to a Unicode string.

    Elements can be equality compared (==) to their Unicode
    representation, their native representation or other elements.

    """

    element_type = _ScalarElement

    def adapt(self, element, value):
        """Given any value, try to coerce it into native format.

        Returns the native format or raises AdaptationError on failure.

        """
        raise NotImplementedError()

    def serialize(self, element, value):
        """Given any value, coerce it into a Unicode representation.

        No special effort is made to coerce values not of native or
        a compatible type.

        *Must* return a Unicode object, always.

        """
        return unicode(value)


class String(Scalar):
    """A regular old Unicode string.

    :arg name: field name
    :arg strip: if ``True``, strip leading and trailing whitespace
                during normalization.

    """

    def __init__(self, name, strip=True, **kw):
        super(String, self).__init__(name, **kw)
        self.strip = strip

    def adapt(self, element, value):
        """Return a Unicode representation.

        If ``strip=True``, leading and trailing whitespace will be
        removed.

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

        If ``strip=True``, leading and trailing whitespace will be
        removed.

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
            raise exc.AdaptationError()
        else:
            if not self.signed:
                if native < 0:
                    raise exc.AdaptationError()
            return native

    def serialize(self, element, value):
        """Generic numeric serialization.

        Converts *value* to a string using Python's string formatting
        function and the :attr:`format` as the template.  The *value*
        is provided to the format as a single, positional format
        argument.

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
    true_synonyms = (u'on', u'true', u'True', u'1')
    false_synonyms = (u'off', u'false', u'False', u'0', u'')

    def __init__(self, name, true=u'1', false=u'', **kw):
        super(Scalar, self).__init__(name, **kw)
        assert isinstance(true, unicode)
        assert isinstance(false, unicode)

        self.true = true
        self.false = false

    def adapt(self, element, value):
        if value == self.true or value in self.true_synonyms:
            return True
        if value == self.false or value in self.false_synonyms:
            return False
        return None

    def serialize(self, element, value):
        return self.true if value else self.false

class Temporal(Scalar):
    type_ = None
    regex = None
    format = None
    used = None

    def __init__(self, name, **kw):
        super(Temporal, self).__init__(name, **kw)

        if 'type_' in kw:
            self.type_ = kw['type_']
        if 'regex' in kw:
            self.regex = kw['regex']
        if 'format' in kw:
            assert isinstance(kw['format'], unicode)
            self.format = kw['format']
        if 'used' in kw:
            self.used = kw['used']

    def adapt(self, element, value):
        if isinstance(value, self.type_):
            return value
        elif isinstance(value, basestring):
            match = self.regex.match(value)
            if not match:
                raise exc.AdaptationError()
            try:
                args = [int(match.group(f)) for f in self.used]
                return self.type_(*args)
            except (TypeError, ValueError), ex:
                raise exc.AdaptationError()
        else:
            raise exc.AdaptationError()

    def serialize(self, element, value):
        if isinstance(value, self.type_):
            return self.format % as_mapping(value)
        else:
            return unicode(value)


class DateTime(Temporal):
    type_ = datetime.datetime
    regex = re.compile(
        ur'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) '
        ur'(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})$')
    format = (u'%(year)04i-%(month)02i-%(day)02i '
              u'%(hour)02i:%(minute)02i:%(second)02i')
    used = ('year', 'month', 'day', 'hour', 'minute', 'second')


class Date(Temporal):
    type_ = datetime.date
    regex = re.compile(
        ur'^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$')
    format = u'%(year)04i-%(month)02i-%(day)02i'
    used = ('year', 'month', 'day')


class Time(Temporal):
    type_ = datetime.time
    regex = re.compile(
        ur'^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})$')
    format = u'%(hour)02i:%(minute)02i:%(second)02i'
    used = ('hour', 'minute', 'second')


class _RefElement(_ScalarElement):
    flattenable = False

    @lazy_property
    def target(self):
        return self.root.el(self.schema.path)

    def _get_u(self):
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
    element_type = _RefElement

    def __init__(self, name, path, writable='ignore', sep='.', **kw):
        super(Ref, self).__init__(name, **kw)

        self.path = self.element_type._parse_element_path(path, sep)
        assert self.path is not None

        self.writable = writable

    def adapt(self, element, value):
        return element.target.schema.adapt(element, value)

    def serialize(self, element, value):
        return element.target.schema.serialize(element, value)
