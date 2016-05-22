class HtmlForm:
    def __init__(self):
        self.html = []
        self.open_form = "<form method='post'>"
        self.close_form = "</form>"
        self.title = ''
        self.target = ''

    def add_text_input(self, prompt, name, value='', element_id=''):
        if element_id != '':
            self.html.append("<p>%s: <input type=text name='%s' value='%s' id='%s'></p>" %
                             (prompt, name, value, element_id))
        else:
            self.html.append("<p>%s: <input type=text name='%s' value='%s'></p>" % (prompt, name, value))

    def add_text_line(self, text):
        self.html.append("<p>%s</p>" % text)

    def add_textarea_input(self, prompt, name, value=''):
        self.html.append("<p>%s: <textarea name='%s'>%s</textarea></p>" % (prompt, name, value))

    def add_hidden_input(self, name, value, element_id=''):
        if element_id != '':
            self.html.append("<input type=hidden name='%s' value='%s' id='%s'>" % (name, value, element_id))
        else:
            self.html.append("<input type=hidden name='%s' value='%s'>" % (name, value))

    def add_select_dropdown(self, prompt, name, options, option_value_name, option_text_name, set_value=None):
        self.html.append("<p>%s: <select name=%s>" % (prompt, name))
        for option in options:
            if str(set_value) == str(option[option_value_name]):
                self.html.append("<option value='%s' selected>%s</option>" % (option[option_value_name],
                                                                              option[option_text_name]))
            else:
                self.html.append("<option value='%s'>%s</option>" % (option[option_value_name],
                                                                     option[option_text_name]))
        self.html.append("</select></p>")

    def add_submit_button(self, value='Submit'):
        self.html.append("<p><input type=submit value='%s'></p>" % value)

    def set_title(self, form_title):
        self.title = form_title

    def print_form(self):
        full_html = [self.open_form]
        if self.title:
            full_html.append("<p><b>%s</b></p>" % self.title)
        full_html.extend(self.html)
        full_html.append(self.close_form)
        for line in full_html:
            print line

    def return_form(self):
        full_html = [self.open_form]
        if self.title:
            full_html.append("<p><b>%s</b></p>" % self.title)
        full_html.extend(self.html)
        full_html.append(self.close_form)
        return full_html


class HtmlTable:
    table_class_default = "<table>"

    def __init__(self, columns=None, table_id=None):
        self.body_rows = []
        self.header = []
        if columns is None:
            self.columns = []
        else:
            self.columns = columns
        self.make_header(self.columns)
        self.table_class = self.table_class_default
        self.close_table = "</table>"
        self.table_id = table_id

    def make_header(self, columns):
        if len(columns) > 0:
            header_html = "<thead><tr id=headerRow>"
            for c in columns:
                header_html += "<th id='%s'>%s</th>" % (c['id'], c['label'])
            header_html += "</tr></thead>"
        else:
            header_html = ""
        self.header = header_html

    def add_row(self, data):
        row_html = "<tr>"
        if type(data) is list:
            for d in data:
                row_html += "<td>%s</td>" % d
        elif type(data) is dict:
            for c in self.columns:
                row_html += "<td>%s</td>" % data[c['id']]
        row_html += "</tr>"
        self.body_rows.append(row_html)

    def add_multiple_rows(self, dataset):
        for d in dataset:
            self.add_row(d)

    def return_table(self):
        open_table = "<table"
        if self.table_class:
            open_table += " class='%s'" % self.table_class
        if self.table_id:
            open_table += " id='%s'" % self.table_id
        open_table += ">"
        full_html = [open_table, self.header, "<tbody>"]
        full_html.extend(self.body_rows)
        full_html.append("</tbody>")
        full_html.append(self.close_table)
        return full_html


class DocumentReadyFunction:
    def __init__(self):
        self.script = []
        self.open_script = "<script type='text/javascript'> $(document).ready(function() {\n"
        self.close_script = "});</script>"

    def add_autocomplete_function(self, variable_name, get_values_function, ac_input_id, value_input_id, item_id):
        self.script.append("var %s = %s;\n" % (variable_name, get_values_function))
        self.script.append("$('%s').autocomplete({\n" % ac_input_id)
        self.script.append("source: %s,\n" % variable_name)
        self.script.append("select: function(evt, ui){\n")
        self.script.append("$('%s').val(ui.item.%s); } });\n" % (value_input_id, item_id))

    def return_script(self):
        full_script = [self.open_script]
        full_script.extend(self.script)
        full_script.append(self.close_script)
        return full_script