
class Entry:
    def __init__(self, name, cursor=None):
        self.children = []
        self.children_map = {}
        self.name = name
        self.cursor = cursor
        self.parent = None
        self.bases = []
        self.template_type_parameters = []

    def has_child(self, name):
        return name in self.children_map

    def add_child(self, entry):
        self.children_map[entry.name] = entry
        self.children.append(entry)
        entry.parent = self
        return entry

    def get_template_decl(self):
        result = "template<"
        first = True
        for ttp in self.template_type_parameters:
            if not first:
                result += ", "
            result += "typename " + ttp.displayname
            first = False
        result += ">"
        return result

    def has_template(self):
        return self.name.find('<') > 0

    def get_full_name(self):
        current = self
        result = ""
        while current and current.name != "$root":
            if current.has_template() and current.parent.has_template():
                result = "::template " + current.name + result
            else:
                result = "::" + current.name + result
            current = current.parent
        return result

