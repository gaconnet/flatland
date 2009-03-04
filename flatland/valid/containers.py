import operator
from ..schema import Slot
from . base import Validator


class NotDuplicated(Validator):
    """A sequence member validator that ensures all sibling values are unique.

    Marks the second and any subsequent occurrences of a value as
    invalid.  Only useful on immediate children of sequence fields
    such as :class:`flatland.List`.

    Example::

      import flatland
      from flatland.valid import NotDuplicated

      schema = flatland.List(
        String('favorite_color', validators=[
          NotDuplicated(failure="Please enter each color only once.")]))

    **Attributes**

    .. attribute:: comparator

      A callable boolean predicate, by default ``operator.eq``.
      Called positionally with two arguments, *element* and *sibling*.

      Can be used as a filter, for example ignoring any siblings that
      have been marked as "deleted" by a checkbox in a web form:

      .. testcode::

        from flatland import Dict, List, String, Integer, Boolean
        from flatland.valid import NotDuplicated

        def live_addrs(element, sibling):
            thisval, thatval = element.value, sibling.value
            # data marked as deleted is never considered a dupe
            if thisval['deleted'] or thatval['deleted']:
                return False
            # compare elements on 'street' & 'city', ignoring 'id'
            return (thisval['street'] == thatval['street'] and
                    thisval['city'] == thatval['city'])

        schema = List('addresses',
                      Dict('address',
                           Integer('id', optional=True),
                           Boolean('deleted'),
                           String('street'),
                           String('city'),
                           validators=[NotDuplicated(comparator=live_addrs)]
                           ))

    .. testcode:: :hide:

        data = {'id': 1, 'deleted': False, 'street': 'a', 'city': 'b'}
        el = schema.create_element(value=[data, data])
        assert not el.validate()
        del el[:]
        el.set([data, dict(data, deleted=True)])
        assert el.validate()

    **Messages**

    .. attribute:: failure

      Emitted on an element that has already appeared in a parent
      sequence.  ``container_label`` will substitute the label of the
      container.  ``position`` is the position of the element in the
      parent sequence, counting up from 1.

    """

    failure = u'%(label)s may not be repeated within %(container_label)s.'

    comparator = operator.eq

    def validate(self, element, state):
        if element.parent is None:
            raise TypeError(
                "%s validator must be applied to a child of a Container "
                "type; %s has no parent." % (
                    type(self).__name__,
                    element.name))
        container = element.parent
        if isinstance(container, Slot):
            container = container.parent
        valid, position = True, 0
        op = self.comparator
        for idx, sibling in enumerate(container.children):
            if sibling is element:
                position = idx + 1
                break
            if valid and op(element, sibling):
                valid = False
        if not valid:
            return self.note_error(
                element, state, 'failure',
                position=position, container_label=container.label)
        return True
