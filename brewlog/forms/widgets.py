from cgi import escape

from wtforms.compat import text_type
from wtforms.widgets.core import HTMLString, html_params

EMPTY_HINTS = [
    ('', ''),
]


def textarea_with_hints(field, **kwargs):
    kwargs.setdefault('id', field.id)
    hints = kwargs.pop('hints', EMPTY_HINTS)
    if not EMPTY_HINTS[0] in hints:
        hints = EMPTY_HINTS + hints
    obj_id = kwargs['id']
    hint_elem_id = '%s_hints' % obj_id
    if len(hints) > 1:
        hint = ['<select %s class="form-control">' % (html_params(id=hint_elem_id))]
        for hint_value, hint_label in hints:
            hint.append('<option value="%s">%s</option>' % (escape(hint_value), escape(hint_label)))
        hint.append('</select>')
        hint = HTMLString(''.join(hint))
    else:
        hint = ''
    textarea = HTMLString('<textarea %s>%s</textarea>' %
        (html_params(name=field.name, **kwargs), escape(text_type(field._value()))))
    if hint:
        script = """
        <script type="text/javascript">
        $("#%(hint_elem_id)s").change(function() {
            var value = $(this).val();
            $("#%(obj_id)s").val(value);
        });
        </script>
        """ % locals()
    else:
        script = ''
    items = [i for i in [hint, textarea, script] if i]
    return HTMLString('<br />'.join(items))
