from operator import attrgetter
from . base import Validator


class Present(Validator):
    missing = u'%(label)s may not be blank.'

    def validate(self, element, state):
        if element.u != u'':
            return True

        return self.note_error(element, state, 'missing')


class IsTrue(Validator):
    false = u'%(label)s must be True.'

    def validate(self, element, state):
        if not bool(element.value):
            return self.note_error(element, state, 'false')
        return True


class IsFalse(Validator):
    true = u'%(label)s must be False.'

    def validate(self, element, state):
        if bool(element.value):
            return self.note_error(element, state, 'true')
        return True


class ValueIn(Validator):
    fail = u'%(value)s is not a valid value for %(label)s.'

    def __init__(self, valid_options, **kw):
        Validator.__init__(self, **kw)
        self.valid_options = valid_options


    def validate(self, element, state):
        if element.value not in self.valid_options:
            return self.note_error(element, state, 'fail')
        return True


class Converted(Validator):
    correct = u'%(label)s is not correct.'

    def validate(self, element, state):
        if element.value is not None:
            return True

        return self.note_error(element, state, 'correct')


class ShorterThan(Validator):
    exceeded = u'%(label)s may not exceed %(maxlength)s characters.'

    def __init__(self, maxlength, **kw):
        Validator.__init__(self, **kw)
        self.maxlength = maxlength

    def validate(self, element, state):
        if len(element.u) > self.maxlength:
            return self.note_error(element, state, 'exceeded')
        return True
NoLongerThan = ShorterThan


class LongerThan(Validator):
    short = u'%(label)s must be at least %(minlength)s characters.'

    def __init__(self, minlength, **kw):
        Validator.__init__(self, **kw)
        self.minlength = minlength

    def validate(self, element, state):
        if len(element.u) < self.minlength:
            return self.note_error(element, state, 'short')
        return True


class LengthBetween(Validator):
    breached = (u'%(label)s must be between %(minlength)s and '
                u'%(maxlength)s characters long.')

    def __init__(self, minlength, maxlength, **kw):
        Validator.__init__(self, **kw)
        self.minlength = minlength
        self.maxlength = maxlength

    def validate(self, element, state):
        l = len(element.u)
        if l < self.minlength or l > self.maxlength:
            return self.note_error(element, state, 'breached')
        return True


class ValueLessThan(Validator):
    """A validator that ensures that the value is less than a limit.

    May be applied to a scalar type such as a :class:`~flatland.Integer`.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValueLessThan

      schema = flatland.Integer('wishes', validators=[ValueLessThan(boundary=4)])

    **Attributes**

    .. attribute:: boundary

      Any object implementing the comparison interface ``__ge__`` and friends

    **Messages**

    .. attribute:: failure

      Emitted if the value is greater than or equal to :attr:`boundary`.
      ``child_label`` will substitute the label of the child schema.

    """

    failure = u'%(label)s must be less than %(boundary)s.'

    def __init__(self, boundary, **kw):
        Validator.__init__(self, **kw)
        self.boundary = boundary

    def validate(self, element, state):
        if not element.value < self.boundary:
            return self.note_error(element, state, 'failure')
        return True


class ValueAtMost(Validator):
    """A validator that enforces a maximum value.

    May be applied to a scalar type such as a :class:`~flatland.Integer`.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValueAtMost

      schema = flatland.Integer('wishes', validators=[ValueAtMost(maximum=3)])

    **Attributes**

    .. attribute:: maximum

      Any object implementing the comparison interface ``__ge__`` and friends

    **Messages**

    .. attribute:: failure

      Emitted if the value is greater than :attr:`maximum`.
      ``child_label`` will substitute the label of the child schema.

    """

    failure = u'%(label)s must be less than or equal to %(maximum)s.'

    def __init__(self, maximum, **kw):
        Validator.__init__(self, **kw)
        self.maximum = maximum

    def validate(self, element, state):
        if not element.value <= self.maximum:
            return self.note_error(element, state, 'failure')
        return True


class ValueGreaterThan(Validator):
    """A validator that ensures that a value is greater than a limit.

    May be applied to a scalar type such as a :class:`~flatland.Integer`.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValueGreaterThan

      schema = flatland.Integer('wishes', validators=[ValueGreaterThan(boundary=4)])

    **Attributes**

    .. attribute:: boundary

      Any object implementing the comparison interface ``__ge__`` and friends

    **Messages**

    .. attribute:: failure

      Emitted if the value is greater than or equal to :attr:`boundary`.
      ``child_label`` will substitute the label of the child schema.

    """

    failure = u'%(label)s must be greater than %(boundary)s.'

    def __init__(self, boundary, **kw):
        Validator.__init__(self, **kw)
        self.boundary = boundary

    def validate(self, element, state):
        if not element.value > self.boundary:
            return self.note_error(element, state, 'failure')
        return True


class ValueAtLeast(Validator):
    """A validator that enforces a minimum value.

    May be applied to a scalar type such as a :class:`~flatland.Integer`.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValueAtLeast

      schema = flatland.Integer('wishes', validators=[ValueAtLeast(minimum=3)])

    **Attributes**

    .. attribute:: minimum

      Any object implementing the comparison interface ``__ge__`` and friends

    **Messages**

    .. attribute:: failure

      Emitted if the value is less than :attr:`minimum`.
      ``child_label`` will substitute the label of the child schema.

    """

    failure = u'%(label)s must be greater than or equal to %(minimum)s.'

    def __init__(self, minimum, **kw):
        Validator.__init__(self, **kw)
        self.minimum = minimum

    def validate(self, element, state):
        if not element.value >= self.minimum:
            return self.note_error(element, state, 'failure')
        return True


class ValueBetween(Validator):
    """A validator that enforces minimum and maximum values.

    May be applied to a scalar type such as a :class:`~flatland.Integer`.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValueBetween

      schema = flatland.Integer('wishes',
                               validators=[ValueBetween(minimum=1, maximum=3)])

    **Attributes**

    .. attribute:: minimum

      Any object implementing the comparison interface ``__ge__`` and friends

    .. attribute:: maximum

      Any object implementing the comparison interface ``__ge__`` and friends

    .. attribute:: inclusive

      Boolean value indicating that :attr:`minimum` and :attr:`maximum` are
      included in the range.  Defaults to True.

    **Messages**

    .. attribute:: failure_inclusive

      Emitted when :attr:`inclusive` is True if the expression
      :attr:`minimum` <= value <= :attr:`maximum`
      evaluates to False.
      ``child_label`` will substitute the label of the child schema.

    .. attribute:: failure_exclusive

      Emitted when :attr:`inclusive` is False if the expression
      :attr:`minimum` < value < :attr:`maximum`
      evaluates to False.
      ``child_label`` will substitute the label of the child schema.

    """

    failure_inclusive = (u'%(label)s must be in the range %(minimum)s '
                         u'to %(maximum)s.')
    failure_exclusive = (u'%(label)s must be greater than %(minimum)s '
                         u'and less than %(maximum)s.')

    inclusive = True

    def __init__(self, minimum, maximum, **kw):
        Validator.__init__(self, **kw)
        self.minimum = minimum
        self.maximum = maximum

    def validate(self, element, state):
        if self.inclusive:
            if not self.minimum <= element.value <= self.maximum:
                return self.note_error(element, state, 'failure_inclusive')
        else:
            if not self.minimum < element.value < self.maximum:
                return self.note_error(element, state, 'failure_exclusive')
        return True


class MapEqual(Validator):
    """A general field equality validator.

    Validates that two or more fields are equal.

    **Attributes**

    .. attribute:: field_paths

      A sequence of field names or field paths.  Path names will be
      evaluated at validation time and relative path names are
      resolved relative to the element holding this validator.  See
      :class:`ValuesEqual` for an example.

    .. attribute:: transform

      A 1-arg callable, passed a
      :class:`~flatland.schema.base.Element`, returning a value for
      equality testing.

    **Messages**

    .. attribute:: unequal

      Emitted if the ``transform(element)`` of all elements are not
      equal.  ``labels`` will substitute to a comma-separated list of
      the :attr:`~flatland.schema.base.Element.label` of all but the
      last element; ``last_label`` is the label of the last.

    """

    unequal = u'%(labels)s and %(last_label)s do not match.'

    field_paths = ()
    transform = lambda el: el

    def __init__(self, *field_paths, **kw):
        """Construct a MapEqual.

        :param \*field_paths: a sequence of 2 or more elements names or paths.

        :param \*\*kw: passed to :meth:`Validator.__init__`.

        """
        if not field_paths:
            assert self.field_paths, 'at least 2 element paths required.'
        else:
            assert len(field_paths) > 1, 'at least 2 element paths required.'
            self.field_paths = field_paths
        Validator.__init__(self, **kw)

    def validate(self, element, state):
        elements = [element.el(name) for name in self.field_paths]
        fn = self.transform
        sample = fn(elements[0])
        if all(fn(el) == sample for el in elements[1:]):
            return True
        labels = ', '.join(el.label for el in elements[:-1])
        last_label = elements[-1].label
        return self.note_error(element, state, 'unequal',
                               labels=labels, last_label=last_label)

class ValuesEqual(MapEqual):
    """Validates that the values of multiple elements are equal.

    A :class:`MapEqual` that compares the
    :attr:`~flatland.schema.base.Element.value` of each element.

    Example:

    .. testcode::

      import flatland
      from flatland.valid import ValuesEqual

      class MyForm(flatland.Form):
          schema = [ String('password'), String('password_again') ]
          validators = ValuesEqual('password', 'password_again')

    .. attribute:: transform()

      attrgettr('value')

    """

    transform = attrgetter('value')


class UnisEqual(MapEqual):
    """Validates that the Unicode values of multiple elements are equal.

    A :class:`MapEqual` that compares the
    :attr:`~flatland.schema.base.Element.u` of each element.

    .. attribute:: transform

      attrgettr('u')

    """

    transform = attrgetter('u')

