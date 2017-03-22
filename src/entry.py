
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
