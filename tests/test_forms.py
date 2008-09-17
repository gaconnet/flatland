from nose.tools import eq_

import flatland as fl


REQUEST_DATA = ((u'abc', u'123'),
                (u'surname', u'SN'),
                (u'xjioj', u'1232'),
                (u'age', u'99'),
                (u'fname', u'FN'),
                (u'ns_fname', u'ns_FN'),
                (u'ns_surname', u'ns_SN'),
                (u'ns_snacks_0_name', u'cheez'),
                (u'ns_snacks_1_name', u'chipz'),
                (u'ns_snacks_2_name', u'chimp'),
                (u'ns_squiznart', u'xyyzy'),
                (u'ns_age', u'23'))

class SimpleForm1(fl.Form):
    schema = [fl.String('fname'),
              fl.String('surname'),
              fl.Integer('age'),
              fl.List('snacks', fl.String('name'))]


def test_straight_parse():
    f = SimpleForm1()
    f.set_flat(REQUEST_DATA)
    eq_(set(f.flatten()),
        set(((u'fname', u'FN'),
             (u'surname', u'SN'),
             (u'age', u'99'))))

    eq_(f.value,
        dict(fname=u'FN',
             surname=u'SN',
             age=99,
             snacks=[]))

def test_namespaced_parse():
    f = SimpleForm1('ns')
    f.set_flat(REQUEST_DATA)

    eq_(set(f.flatten()),
        set(((u'ns_fname', u'ns_FN'),
             (u'ns_surname', u'ns_SN'),
             (u'ns_age', u'23'),
             (u'ns_snacks_0_name', u'cheez'),
             (u'ns_snacks_1_name', u'chipz'),
             (u'ns_snacks_2_name', u'chimp'))))

    eq_(f.value,
        dict(fname=u'ns_FN',
             surname=u'ns_SN',
             age=23,
             snacks=[u'cheez', u'chipz', u'chimp']))

    assert f['age'].value == 23
    assert f['age'].u == u'23'



