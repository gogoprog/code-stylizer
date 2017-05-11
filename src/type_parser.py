import sys
import os

class Type(object):

    def __init__(self, text):
        self.text = text.strip()
        self.left = None
        self.templates = []

    def get_parented_string(self):
        result = self.get_string()
        left = self.left

        while left != None:
            result = left.get_string() + "::" + result
            left = left.left

        return result

    def get_string(self):
        result = self.text

        if len(self.templates) > 0:
            result += "<"
            first = True
            for template in self.templates:
                if not first:
                    result += ", "
                result += template.get_parented_string()
                first = False
            result += ">"

        return result

def parse(str):
    index = 0
    length = len(str)
    next_type_index = 0
    previous_index = 0
    current_type = None
    while index < len(str):
        next_colons = str.find("::", index)
        next_open_template = str.find("<", index)
        previous_index = index

        if next_colons == -1:
            next_type_index = length
            index = length
        else:
            index = next_colons + 2
            next_type_index = next_colons

        if next_open_template < next_type_index and next_open_template != -1:
            open_count = 1
            index = next_open_template + 1
            first_open_template = next_open_template
            new_type = Type(str[previous_index:first_open_template])
            type_start = first_open_template + 1

            while open_count > 0:
                next_open_template = str.find("<", index)
                next_close_template = str.find(">", index)
                next_comma = str.find(",", index)

                if open_count == 1 and next_comma != -1:
                    if next_comma < next_open_template or next_open_template == -1:
                        if next_comma < next_close_template or next_close_template == -1:
                            template_str = str[type_start:next_comma]
                            new_type.templates.append(parse(template_str))
                            type_start = next_comma + 1

                if next_open_template > next_close_template or next_open_template == -1:
                    open_count -= 1
                    index = next_close_template + 1

                    if open_count == 0:
                        template_str = str[type_start:index-1]
                        new_type.templates.append(parse(template_str))

                elif next_open_template != -1 and next_open_template < next_close_template:
                    open_count += 1
                    index = next_open_template + 1
                else:
                    assert(False)

        else:
            new_type = Type(str[previous_index:next_type_index])

        new_type.left = current_type
        current_type = new_type

    return current_type
