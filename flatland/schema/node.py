import operator


class Node(object):
    flattenable = False

    def __init__(self, schema, parent=None, **kw):
        self.schema = schema
        self.parent = parent

        self.errors = []
        self.warnings = []

    @property
    def name(self):
        return self.schema.name

    @property
    def label(self):
        return self.schema.label

    @property
    def path(self):
        "A tuple of node names, starting at this node's topmost parent."
        p, node = [], self
        while node is not None:
            if node.name is not None:
                p.append(node.name)
            node = node.parent

        return tuple(reversed(p))

    @property
    def root(self):
        node = self
        while node is not None:
            if node.parent is None:
                break
            node = node.parent
        return node

    def fq_name(self, sep='_'):
        """
        Joins this node's path with sep and return the fully qualified,
        flattened name.
        """
        return sep.join(self.path)

    def el(self, path, sep=u'.'):
        search = self._parse_node_path(path, sep)
        if search is None:
            raise KeyError(u'No element at "%s".' % path)

        try:
            return self._el(search)
        except KeyError:
            raise KeyError(u'No element found at "%s"' % path)

    def _el(self, path):
        raise NotImplementedError()

    @classmethod
    def _parse_node_path(self, path, sep):
        if isinstance(path, basestring):
            steps = path.split(sep)
        elif isinstance(path, (list, tuple)) or hasattr('next', path):
            steps = path
        else:
            return None

        return [None if step in (u'""', u"''") else step for step in steps]


    ## Errors and warnings- any node can have them.
    def add_error(self, message):
        "Register an error message on this node, ignoring duplicates."
        if message not in self.errors:
            self.errors.append(message)

    def add_warning(self, message):
        "Register a wawrning message on this node, ignoring duplicates."
        if message not in self.warnings:
            self.warnings.append(message)

    ## Element value and wrangling
    def apply(self, func, data=None, depth_first=False):
        return [func(self, data)]

    def flatten(self, sep=u'_', value=lambda node: node.u):
        pairs = []
        def serialize(node, data):
            if node.flattenable:
                data.append((node.fq_name(sep), value(node)))

        self.apply(serialize, pairs)
        return pairs

    def set(self, value):
        raise NotImplementedError()

    def set_flat(self, pairs, sep='_'):
        """
        Given a sequence of name/value tuples or a dict, build out a
        structured tree of value nodes.
        """
        if hasattr(pairs, 'items'):
            pairs = pairs.items()

        return self._set_flat(pairs, sep)

    def _set_flat(self, pairs, sep):
        raise NotImplementedError()

    def validate(self, state=None, recurse=True, validators=None):
        if not recurse:
            return self._validate(state, validators=validators)

        def collector(node, _):
            return node._validate(state=state, validators=None)

        return reduce(operator.and_, self.apply(collector, None), True)

    def _validate(self, state=None, validators=None):
        if validators is None:
            if not self.schema.validators:
                return True
        validators = self.schema.validators

        if not isinstance(validators, (tuple, list)):
            validators = validators,

        valid = True
        for v in validators:
            valid &= v(self, state)
            if not valid:
                return False

        return valid
