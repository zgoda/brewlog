from html import escape

from markupsafe import Markup
from wtforms.compat import text_type
from wtforms.widgets.core import html_params

EMPTY_HINTS = [
    ('', ''),
]


def textarea_with_hints(field, **kwargs):
    kwargs.setdefault('id', field.id)
    hints = kwargs.pop('hints', EMPTY_HINTS)
    if not EMPTY_HINTS[0] in hints:
        hints = EMPTY_HINTS + hints
    obj_id = kwargs['id']
    hint_elem_id = f'{obj_id}_hints'
    if len(hints) > 1:
        hint = [f'<select {html_params(id=hint_elem_id)} class="form-control">']
        for hint_value, hint_label in hints:
            hint.append(
                f'<option value="{escape(hint_value)}">{escape(hint_label)}</option>'
            )
        hint.append('</select>')
        hint = Markup(''.join(hint))
    else:
        hint = ''
    textarea = Markup(
        f'<textarea {html_params(name=field.name, **kwargs)}>'
        f'{escape(text_type(field._value()))}</textarea>'
    )
    if hint:
        script = f"""
        <script type="text/javascript">
        $("#{hint_elem_id}").change(function() {{
            var value = $(this).val();
            $("#{obj_id}").val(value);
        }});
        </script>
        """
    else:
        script = ''
    items = [i for i in [hint, textarea, script] if i]
    return Markup('<br />'.join(items))
