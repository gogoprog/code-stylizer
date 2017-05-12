from conversions import Case, get_conversion

class Type(object):

    def __init__(self, text):
        self.text = text.strip()
        self.left = None
        self.templates = []

    def get_parented_string(self, case):
        result = self.get_string(case)
        left = self.left

        while left != None:
            result = left.get_string(case) + "::" + result
            left = left.left

        return result

    def get_string(self, case):

        result = get_conversion(self.text, Case.SNAKE, case)

        if len(self.templates) > 0:
            result += "<"
            first = True
            for template in self.templates:
                if not first:
                    result += ", "
                result += template.get_parented_string(case)
                first = False
            result += ">"

        return result
