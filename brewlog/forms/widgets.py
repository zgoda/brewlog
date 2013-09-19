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
    hint = ['<select %s>' % (html_params(id=hint_elem_id))]
    for hint_value, hint_label in hints:
        hint.append('<option value="%s">%s</option>' % (escape(hint_value), escape(hint_label)))
    hint.append('</select>')
    hint = HTMLString(''.join(hint))
    textarea = HTMLString('<textarea %s>%s</textarea>' % (html_params(name=field.name, **kwargs), escape(text_type(field._value()))))
    script = """
    <script type="text/javascript">
    $("#%(hint_elem_id)s").change(function() {
        var value = $(this).val();
        $("#%(obj_id)s").val(value);
    });
    </script>
    """ % locals()
    return HTMLString('<br />'.join([hint, textarea, script]))
