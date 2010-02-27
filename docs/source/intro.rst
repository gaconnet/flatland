.. -*- fill-column: 78 -*-

========
Overview
========

Philosphy
---------

flatland's design stems from a few basic tenets:

 - All input is suspect
 - Input can come from multiple sources and interfaces
 - Bad input isn't exceptional: it is expected

With flatland, you describe exactly what elements your form may contain.
Forms extract and process only their known elements out of the ``(key,
value)`` input data.  Unexpected or malicious data will not be processed.

The description of forms and their fields is data-centric rather than HTML or
interface-centric.  In a flatland form schema, a password input field is
simply a string, not a "PasswordInput" or the like. The decision about how to
represent that field is left up to another layer entirely.  Maybe you do want
an ``<input type="password">`` control, or maybe ``<input type="hidden">`` in
some cases, or sometimes the data is coming in as JSON.  flatland can act as
another type of M in your M/VC, MC, MVC or MTV.

Humans are imperfect and filling out forms will always be
error-prone. flatland recognizes this and provides features to make error
detection and correction part of the regular workflow of a form.  By default,
validation routines will consider every element of a form and mark all
problematic fields, allowing users to take action on all issues at once.

Introduction
------------

Field schemas define all possible fields the form may contain.  A schema may a
single field, a collection of fields, or an even richer structure.  Nested
mappings and lists of fields are supported, as well as compound fields and
even more exotic types.

.. testcode::

  from flatland import Form, String

  class SignInForm(Form):
      username = String
      password = String

Field schemas are long-lived objects similar to class definitions.  The
instantiations of a flatland schema are called data elements, a tree structure
of data-holding objects.  The elements of a flatland form may be initiated
blank, using default values, or with values taken from your objects.

.. testsetup::

  class Mock(object):
      def __getattr__(self, key):
          return lambda *a, **kw: None
  request = logging = Mock()
  request.POST = [('username', 'jek'), ('password', 'p1')]
  redirect = request.redirect

.. testcode::

  form = SignInForm.from_flat(request.POST)
  if form.validate():
      logging.info(u"sign-in: %s" % form.el('username'))
      redirect('/app/')
  else:
      render('login.html', form=form)

Elements are rich objects that validate and normalize input data as well as
hold field-level error and warning messages.  Elements can be exported to a
native Python structure, flattened back into Unicode key, value pairs or used
as-is in output templates for form layout, redisplay and error reporting.

.. doctest::

  >>> as_regular_python_data = form.value
  >>> type(as_regular_python_data)
  <type 'dict'>
  >>> as_regular_python_data['username']
  u'jek'
  >>> form2 = SignInForm(as_regular_python_data)
  >>> assert form['username'].value == form2['username'].value

License
-------

flatland is free software distributed under the MIT License.

History
-------

flatland is a Python implementation of techniques I've been using for form and
web data processing for ages, in many different languages.  It is an immediate
conceptual decendent and re-write of "springy", a closed-source library used
interally at Virtuous, Inc.  The Genshi filter support was donated to the
flatland project by Virtuous.
