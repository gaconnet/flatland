from flatland import String

from genshi.template.base import TemplateSyntaxError

from tests._util import assert_raises
from tests.markup._util import render_genshi_06 as render, need


schema = String.named('element')


@need('genshi_06')
def setup():
    pass


def test_version_sensor():
    from flatland.out import genshi_06
    template = 'not a Genshi 0.6 template'
    assert_raises(RuntimeError, genshi_06.setup, template)


def test_bogus_tags():
    for snippet in [
        u'<form:auto-name/>',
        u'<form:auto-value/>',
        u'<form:auto-domid/>',
        u'<form:auto-for/>',
        u'<form:auto-tabindex/>',
        ]:
        assert_raises(TemplateSyntaxError, render, snippet, 'xml', schema)


def test_bogus_elements():
    for snippet in [
        u'<div form:with="snacks" />',
        u'<div form:set="snacks" />',
        ]:
        assert_raises(TemplateSyntaxError, render, snippet, 'xml', schema)


def test_directive_ordering():
    markup = """\
<form form:bind="form" py:if="True">
  <input form:bind="form" py:if="False"/>
  <input py:with="foo=form" form:bind="foo" />
</form>
"""
    expected = """\
<form name="element">
  <input name="element" value="" />
</form>"""

    rendered = render(markup, 'xhtml', schema)
    assert rendered == expected


def test_attribute_interpolation():
    markup = """\
<input py:with="flag='on'" form:bind="form" form:auto-domid="${flag}" />
<input py:with="var='n'" form:bind="form" form:auto-domid="o${var}" />
"""
    expected = """\
<input name="element" value="" id="f_element" />
<input name="element" value="" id="f_element" />"""

    rendered = render(markup, 'xhtml', schema)
    assert rendered == expected


def test_pruned_tag():
    markup = """\
<form:with auto-name="off" py:if="False">xxx</form:with>
"""
    expected = ""

    rendered = render(markup, 'xhtml', schema)
    assert rendered == expected


def test_attributes_preserved():
    markup = """\
<div xmlns:xyzzy="yo">
  <input xyzzy:blat="pow" class="abc" form:bind="form" />
</div>
"""
    expected = """\
<div xmlns:xyzzy="yo">
  <input xyzzy:blat="pow" class="abc" name="element" value="" />
</div>"""

    rendered = render(markup, 'xhtml', schema)
    assert rendered == expected


def test_attribute_removal():
    markup = """\
<input type="checkbox" form:bind="form" value="xyzzy" checked="checked" />
"""
    expected = """\
<input type="checkbox" value="xyzzy" name="element" />"""

    rendered = render(markup, 'xhtml', schema)
    assert rendered == expected


def test_tortured_select():
    markup = """\
<select form:bind="form">
  <option value="hit"/>
  <option value="miss"/>
  <option value="hit" form:bind=""/>
  <optgroup label="nested">
    <option>
      h${"i"}t
    </option>
    <option value="miss"/>
  </optgroup>
  <optgroup label="nested">
    <option value="hit" form:bind=""/>
  </optgroup>
  <option value="hit" py:if="True">
    <option value="hit">
      <option value="hit" form:bind="form" py:if="True"/>
    </option>
  </option>
</select>
    """

    expected = """\
<select name="element">
  <option value="hit" selected="selected"></option>
  <option value="miss"></option>
  <option value="hit"></option>
  <optgroup label="nested">
    <option selected="selected">
      hit
    </option>
    <option value="miss"></option>
  </optgroup>
  <optgroup label="nested">
    <option value="hit"></option>
  </optgroup>
  <option value="hit" selected="selected">
    <option value="hit" selected="selected">
      <option value="hit" selected="selected"></option>
    </option>
  </option>
</select>"""

    factory = schema.using(default=u'hit').from_defaults
    rendered = render(markup, 'xhtml', factory)
    if rendered != expected:
        print "\n" + __name__
        print "Expected:\n" + expected
        print "Got:\n" + rendered
    assert rendered == expected
