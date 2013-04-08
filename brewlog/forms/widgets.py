# -*- coding: utf-8 -*-

__revision__ = '$Id$'


from wtforms.widgets import TableWidget
from wtforms.widgets import html_params, HTMLString
from wtforms.compat import text_type


class SubformTableWidget(TableWidget):

    def __call__(self, field, **kwargs):
        kwargs['class_'] = 'subform-table'
        html = []
        if self.with_table_tag:
            kwargs.setdefault('id', field.id)
            html.append('<table %s>' % html_params(**kwargs))
        hidden = ''
        header_row = ['<tr>']
        cell_row = ['<tr>']
        for subfield in field:
            if subfield.type == 'HiddenField':
                hidden += text_type(subfield)
            else:
                header_row.append('<th>%s</th>' % text_type(subfield.label))
                cell_row.append('<td>%s%s</td>' % (hidden, text_type(subfield)))
                hidden = ''
        header_row.append('<th>&nbsp;</th>')
        cell_row.append('<td class="item-ops"><a href="#" class="add-item">(+)</a> <a href="#" class="remove-item">(-)</a></td>')
        header_row.append('</tr>')
        cell_row.append('</tr>')
        html.append(''.join(header_row))
        html.append(''.join(cell_row))
        if self.with_table_tag:
            html.append('</table>')
        if hidden:
            html.append(hidden)
        return HTMLString(''.join(html))
