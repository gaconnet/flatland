from nose.tools import eq_, assert_raises, set_trace

from flatland import schema


def test_from_object():
    class Obj(object):
        def __init__(self, **kw):
            for (k, v) in kw.items():
                setattr(self, k, v)

    class Form(schema.Form):
        schema = [schema.String('x'),
                  schema.String('y')]

    from_obj = lambda obj, **kw: Form.from_object(obj, **kw).value

    eq_(from_obj(None), dict(x=None, y=None))
    eq_(from_obj([]), dict(x=None, y=None))
    eq_(from_obj(123), dict(x=None, y=None))

    eq_(from_obj(Obj()), dict(x=None, y=None))

    eq_(from_obj(Obj(x='x!')), dict(x='x!', y=None))
    eq_(from_obj(Obj(x='x!', y='y!')), dict(x='x!', y='y!'))
    eq_(from_obj(Obj(x='x!', z='z!')), dict(x='x!', y=None))

    eq_(from_obj(Obj(x='x!', y='y!'), include=['x']),
        dict(x='x!', y=None))
    eq_(from_obj(Obj(x='x!', y='y!'), omit=['y']),
        dict(x='x!', y=None))

    eq_(from_obj(Obj(x='x!', z='z!'), rename={'z': 'y'}),
        dict(x='x!', y='z!'))

    eq_(from_obj(Obj(x='x!', z='z!'), rename={'z': 'x'}),
        dict(x='z!', y=None))

    eq_(from_obj(Obj(x='x!', z='z!'), rename={'z': 'z'}),
        dict(x='x!', y=None))

    eq_(from_obj(Obj(x='x!', z='z!'), rename={'x': 'z'}),
        dict(x=None, y=None))


def test_composition():
    class Inner(schema.Form):
        schema = [
            schema.String('sound', default='bleep')
            ]

    class Outer(schema.Form):
        schema = [
            Inner('in'),
            schema.String('way_out', default='mooooog')
            ]

    unset = {'in': {'sound': None}, 'way_out': None}
    wanted = {'in': {'sound': 'bleep'}, 'way_out': 'mooooog'}

    el = Outer.from_defaults()
    eq_(el.value, wanted)

    el = Outer.create_blank()
    eq_(el.value, unset)

    el.set(wanted)
    eq_(el, wanted)
