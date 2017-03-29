from clang.cindex import CursorKind, Diagnostic, TranslationUnit

class Entry:
    def __init__(self, name, cursor=None):
        self.children = []
        self.children_map = {}
        self.name = name
        self.cursor = cursor
        self.parent = None
        self.bases = []

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
        for child in self.cursor.get_children():
            if child.kind == CursorKind.TEMPLATE_TYPE_PARAMETER:
                if not first:
                    result += ", "
                result += "typename " + child.displayname
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

    def get_full_parent(self):
        current = self.parent
        result = ""
        while current and current.name != "$root":
            if current.has_template() and current.parent.has_template():
                result = "::template " + current.name + result
            else:
                result = "::" + current.name + result
            current = current.parent
        return result

