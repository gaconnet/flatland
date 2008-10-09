import datetime
from tests.genshi._util import (
    RenderTest, FilteredRenderTest, from_text_files, from_docstring)
import flatland


def small_form(values=None):
    schema = flatland.Dict(
        None,
        flatland.String('field1'),
        flatland.String('field2'),
        flatland.Boolean('toggle1'),
        flatland.Boolean('toggle2'),
        flatland.Array(flatland.String('multi')),
        flatland.DateYYYYMMDD('date1'),
        )
    if values is None:
        values = {
            'field1': 'val',
            'toggle2': True,
            'multi': ['a', 'b'],
            'date1': datetime.date(1999, 12, 31),
            }
    el = schema.create_element(value=values)
    return {'form': el}

class TestUnfilteredTags(RenderTest):
    @from_docstring(context_factory=small_form)
    def test_any(self):
        """
:: test
${form.field1.bind}
:: eq
form.el(u'.field1')
:: endtest

:: test
<div id="${type(form.field1.bind).__name__}">x</div>
:: eq
<div id="WrappedElement">x</div>
:: endtest

:: test
<div id="${unicode(form.field1.bind)}">x</div>
:: eq
<div id="form.el(u'.field1')">x</div>
:: endtest

:: test
<div id="${form.field1.bind}">x</div>
:: eq
<div id="form.el(u'.field1')">x</div>
:: endtest

:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" form:bind="form.el(u'.field1')" />
:: endtest

:: test
<input type="text" form:bind="${form.field1.bind}" name="x"/>
:: eq
<input type="text" form:bind="form.el(u'.field1')" name="x"/>
:: endtest
        """


class TestTags(FilteredRenderTest):
    def setup(self):
        from flatland import Dict, String
        self.schema = Dict(None, String('field'))

    @from_docstring(context_factory=small_form)
    def test_empty(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq  # sneaky
<input type="text" form:bind="form.el(u'.field1')" />
:: endtest

:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="field1" value="val" />
:: endtest
        """

    @from_docstring(context_factory=small_form)
    def test_auto_name(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test
<form:with auto-name="off">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" value="val" />
:: endtest

:: test default fallback
<form:with auto-name="auto">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test full explicit default fallback
<form:with auto-name="auto">
<input type="text" form:bind="${form.field1.bind}" form:auto-name="auto" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test local on
<input type="text" form:bind="${form.field1.bind}" form:auto-name="on"/>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test local off
<input type="text" form:bind="${form.field1.bind}" form:auto-name="off"/>
:: eq
<input type="text" value="val" />
:: endtest

:: test existing attribute wins over context on
<input type="text" name="foo" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="foo" value="val" />
:: endtest

:: test local on squeezes out existing attribute
<input type="text" name="foo" form:bind="${form.field1.bind}"
  form:auto-name="on"/>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test context on
<form:with auto-domid="on">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" id="f_field1" name="field1" value="val" />
:: endtest

:: test named form
<form form:bind="${form.field1.bind}" />
:: eq
<form name="field1" />
:: endtest

:: test anonymous form
<form form:bind="${form.bind}" />
:: eq
<form />
:: endtest


        """

    @from_docstring(context_factory=small_form)
    def test_auto_domid(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test
<form:with auto-domid="off">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test default fallback
<form:with auto-domid="auto">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test full explicit default fallback
<form:with auto-domid="auto">
<input type="text" form:bind="${form.field1.bind}" form:auto-domid="auto" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test local on
<input type="text" form:bind="${form.field1.bind}" form:auto-domid="on"/>
:: eq
<input type="text" id="f_field1" name="field1" value="val" />
:: endtest

:: test context on
<form:with auto-domid="on">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" id="f_field1" name="field1" value="val" />
:: endtest

        """

    @from_docstring(context_factory=small_form)
    def test_auto_for(self):
        """
:: test
<label form:bind="${form.field1.bind}" />
:: eq
<label />
:: endtest

:: test
<form:with auto-domid="off">
<label form:bind="${form.field1.bind}" />
</form:with>
:: eq
<label />
:: endtest

:: test default fallback
<form:with auto-domid="auto">
<label form:bind="${form.field1.bind}" />
</form:with>
:: eq
<label />
:: endtest

:: test full explicit default fallback
<form:with auto-domid="auto">
<label form:bind="${form.field1.bind}" form:auto-domid="auto" />
</form:with>
:: eq
<label />
:: endtest

:: test local on
<label form:bind="${form.field1.bind}" form:auto-for="on"/>
:: eq
<label for="f_field1" />
:: endtest

:: test context on
<form:with auto-domid="on">
<label form:bind="${form.field1.bind}" />
</form:with>
:: eq
<label for="f_field1" />
:: endtest

        """

    @from_docstring(context_factory=small_form)
    def test_auto_tabindex(self):
        """
:: test
<form:with auto-tabindex="on">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test
<form:with auto-tabindex="on" tabindex="0">
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test
<form:with auto-tabindex="on" tabindex="1">
<input type="text" form:bind="${form.field1.bind}" />
<input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
<input type="text" tabindex="1" name="field1" value="val" />
<input type="text" tabindex="2" name="field1" value="val" />
:: endtest

:: test
<form:with tabindex="1">
<input type="text" form:bind="${form.field1.bind}" form:auto-tabindex="off" />
<input type="text" form:bind="${form.field1.bind}" />
<input type="text" form:bind="${form.field1.bind}" form:auto-tabindex="on" />
</form:with>
:: eq
<input type="text" name="field1" value="val" />
<input type="text" name="field1" value="val" />
<input type="text" tabindex="1" name="field1" value="val" />
:: endtest

:: test
<form:with tabindex="50">
<div form:auto-tabindex="on" />
</form:with>
:: eq
<div tabindex="50" />
:: endtest

:: test
<form:with auto-tabindex="on" tabindex="100">
  <input type="text" form:bind="${form.field1.bind}" />
  <form:with tabindex="50">
    <input type="text" form:bind="${form.field1.bind}" />
  </form:with>
  <input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <input type="text" tabindex="100" name="field1" value="val" />
    <input type="text" tabindex="50" name="field1" value="val" />
  <input type="text" tabindex="101" name="field1" value="val" />
:: endtest

:: test
<form:with auto-tabindex="on" tabindex="100">
  <input type="text" form:bind="${form.field1.bind}" />
  <form:with tabindex="0">
    <input type="text" form:bind="${form.field1.bind}" />
  </form:with>
  <input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <input type="text" tabindex="100" name="field1" value="val" />
    <input type="text" name="field1" value="val" />
  <input type="text" tabindex="101" name="field1" value="val" />
:: endtest

:: test
<form:with auto-tabindex="on" tabindex="1">
  <input type="text" form:bind="${form.field1.bind}" />
  <input type="text" form:bind="${form.field1.bind}" tabindex="2" />
  <input type="text" form:bind="${form.field1.bind}" />
  <input type="text" form:bind="${form.field1.bind}" tabindex="-1" />
  <input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <input type="text" tabindex="1" name="field1" value="val" />
  <input type="text" tabindex="2" name="field1" value="val" />
  <input type="text" tabindex="2" name="field1" value="val" />
  <input type="text" tabindex="-1" name="field1" value="val" />
  <input type="text" tabindex="3" name="field1" value="val" />
:: endtest

    """

    @from_docstring(context_factory=small_form)
    def test_auto_value_forced(self):
        """
:: test unbound
<input type="text" form:auto-value="on" />
:: eq
<input type="text" />
:: endtest

:: test unknown
<div form:bind="${form.field1.bind}" form:auto-value="on" />
:: eq
<div value="val" />
:: endtest
        """

    @from_docstring(context_factory=small_form)
    def test_auto_value_input(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="field1" value="val" />
:: endtest

:: test
<input type="password" form:bind="${form.field1.bind}" />
:: eq
<input type="password" name="field1" value="val" />
:: endtest

:: test
<input type="hidden" form:bind="${form.field1.bind}" />
:: eq
<input type="hidden" name="field1" value="val" />
:: endtest

:: test
<input type="submit" form:bind="${form.field1.bind}" />
:: eq
<input type="submit" name="field1" value="val" />
:: endtest

:: test
<input type="reset" form:bind="${form.field1.bind}" />
:: eq
<input type="reset" name="field1" value="val" />
:: endtest

:: test
<input type="image" form:bind="${form.field1.bind}" />
:: eq
<input type="image" name="field1" />
:: endtest

:: test
<input type="image" form:bind="${form.field1.bind}" form:auto-value="on" />
:: eq
<input type="image" name="field1" value="val" />
:: endtest

:: test
<input type="button" form:bind="${form.field1.bind}" />
:: eq
<input type="button" name="field1" value="val" />
:: endtest

:: test
<input type="file" form:bind="${form.field1.bind}" />
:: eq
<input type="file" name="field1" />
:: endtest

:: test
<input type="file" form:bind="${form.field1.bind}" form:auto-value="on" />
:: eq
<input type="file" name="field1" value="val" />
:: endtest

:: test
<input type="unknown" form:bind="${form.field1.bind}" />
:: eq
<input type="unknown" name="field1" />
:: endtest

:: test
<input type="unknown" form:bind="${form.field1.bind}" form:auto-value="on" />
:: eq
<input type="unknown" name="field1" value="val" />
:: endtest

:: test compound
<input type="text" form:bind="${form.date1.bind}" />
:: eq
<input type="text" name="date1" value="1999-12-31" />
:: endtest

    """

    @from_docstring(context_factory=small_form)
    def test_auto_value_input_checkbox(self):
        """
:: test
<input type="checkbox" form:bind="${form.field1.bind}" />
:: eq
<input type="checkbox" name="field1" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.field1.bind}" value="val" />
:: eq
<input type="checkbox" value="val" name="field1" checked="checked" />
:: endtest

:: test scalar value miss strips CHECKED
<input type="checkbox" form:bind="${form.field1.bind}" value="x" checked="checked"/>
:: eq
<input type="checkbox" value="x" name="field1" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.toggle1.bind}" />
:: eq
<input type="checkbox" name="toggle1" value="1" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.toggle2.bind}" />
:: eq
<input type="checkbox" name="toggle2" value="1" checked="checked" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.multi.bind}" />
:: eq
<input type="checkbox" name="multi" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.multi.bind}" value="a" />
:: eq
<input type="checkbox" value="a" name="multi" checked="checked" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.multi.bind}" value="b" />
:: eq
<input type="checkbox" value="b" name="multi" checked="checked" />
:: endtest

:: test
<input type="checkbox" form:bind="${form.multi.bind}" value="c" />
:: eq
<input type="checkbox" value="c" name="multi" />
:: endtest

:: test container value misses strip CHECKED
<input type="checkbox" form:bind="${form.multi.bind}" value="c" checked="checked" />
:: eq
<input type="checkbox" value="c" name="multi" />
:: endtest

        """

    @from_docstring(context_factory=small_form)
    def test_auto_value_input_radio(self):
        """
:: test element values don't emit value=
<input type="radio" form:bind="${form.field1.bind}" />
:: eq
<input type="radio" name="field1" />
:: endtest

:: test checked if element value matches literal value=
<input type="radio" form:bind="${form.field1.bind}" value="val" />
:: eq
<input type="radio" value="val" name="field1" checked="checked" />
:: endtest

:: test not checked if element value doesn't match literal value=
<input type="radio" form:bind="${form.field1.bind}" value="other" />
:: eq
<input type="radio" value="other" name="field1" />
:: endtest

:: test no special boolean treatment
<input type="radio" form:bind="${form.toggle2.bind}" />
:: eq
<input type="radio" name="toggle2" />
:: endtest

:: test
<input type="radio" form:bind="${form.multi.bind}" />
:: eq
<input type="radio" name="multi" />
:: endtest

:: test
<input type="radio" form:bind="${form.multi.bind}" value="a" />
:: eq
<input type="radio" value="a" name="multi" checked="checked" />
:: endtest

:: test
<input type="radio" form:bind="${form.multi.bind}" value="b" />
:: eq
<input type="radio" value="b" name="multi" checked="checked" />
:: endtest

:: test
<input type="radio" form:bind="${form.multi.bind}" value="c" />
:: eq
<input type="radio" value="c" name="multi" />
:: endtest

:: test container value misses strip CHECKED
<input type="radio" form:bind="${form.multi.bind}" value="c" checked="checked" />
:: eq
<input type="radio" value="c" name="multi" />
:: endtest

        """

    @from_docstring(context_factory=small_form)
    def test_auto_value_input_overrides(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" value="local" />
:: eq
<input type="text" value="local" name="field1" />
:: endtest

:: test
<form:with auto-value="off">
  <input type="text" form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <input type="text" name="field1" />
:: endtest
        """

    @from_docstring(context_factory=lambda: small_form({}))
    def test_auto_value_input_unset(self):
        """
:: test
<input type="text" form:bind="${form.field1.bind}" />
:: eq
<input type="text" name="field1" value="" />
:: endtest
    """

    @from_docstring(context_factory=small_form)
    def test_auto_value_select(self):
        """
:: test
<select form:bind="${form.field1.bind}" />
:: eq
<select name="field1" />
:: endtest

:: test unmatched option forms are unmolested
<select form:bind="${form.field1.bind}">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option>baz</option>
</select>
:: eq
<select name="field1">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option>baz</option>
</select>
:: endtest

:: test basic match on unadorned option
<select form:bind="${form.field1.bind}">
  <option value="val"/>
  <option value="bar">Bar</option>
  <option>baz</option>
</select>
:: eq
<select name="field1">
  <option value="val" selected="selected" />
  <option value="bar">Bar</option>
  <option>baz</option>
</select>
:: endtest

:: test matched option w/ stream passes on stream
<select form:bind="${form.field1.bind}">
  <option value="foo"/>
  <option value="val">Bar</option>
  <option>baz</option>
</select>
:: eq
<select name="field1">
  <option value="foo"/>
  <option value="val" selected="selected">Bar</option>
  <option>baz</option>
</select>
:: endtest

:: test match option w/ only stream as a value
<select form:bind="${form.field1.bind}">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option>val</option>
</select>
:: eq
<select name="field1">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option selected="selected">val</option>
</select>
:: endtest

:: test stream matches are not sensitive to surrounding whitespace
<select form:bind="${form.field1.bind}">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option>
    val
  </option>
</select>
:: eq
<select name="field1">
  <option value="foo"/>
  <option value="bar">Bar</option>
  <option selected="selected">
    val
  </option>
</select>
:: endtest

"""

    @from_docstring(context_factory=small_form)
    def test_auto_value_button(self):
        """
:: test
<button form:bind="${form.field1.bind}" />
:: eq
<button name="field1">val</button>
:: endtest

:: test
<form:with auto-value="off">
  <button form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <button name="field1" />
:: endtest

:: test child value overrides
<button form:bind="${form.field1.bind}">local</button>
:: eq
<button name="field1">local</button>
:: endtest

:: test attribute value overrides
<button form:bind="${form.field1.bind}" value="local"/>
:: eq
<button value="local" name="field1" />
:: endtest

:: test force follows value specification style
<button form:bind="${form.field1.bind}" value="local" form:auto-value="on" />
:: eq
<button value="val" name="field1" />
:: endtest

    """

    @from_docstring(context_factory=small_form)
    def test_auto_value_textarea(self):
        """
:: test
<textarea form:bind="${form.field1.bind}" />
:: eq
<textarea name="field1">val</textarea>
:: endtest

:: test
<form:with auto-value="off">
  <textarea form:bind="${form.field1.bind}" />
</form:with>
:: eq
  <textarea name="field1" />
:: endtest

:: test child value overrides
<textarea form:bind="${form.field1.bind}">local</textarea>
:: eq
<textarea name="field1">local</textarea>
:: endtest

    """

