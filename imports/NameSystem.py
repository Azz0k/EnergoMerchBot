import re


class NameSystem:
    def __init__(self):
        self.forward = dict()
        self.reverse = dict()
        self.index = 0
        self.pattern = '[ _-]+'

    def add_string_to_ns(self, element: str):
        for el in re.split(self.pattern, element):
            self.add_element(el)

    def forward_replace(self, element: str):
        result = [self.get_forward(x) for x in re.split(self.pattern, element)]
        return '_'.join(result)

    def reverse_replace(self, element: str):
        result = [self.get_reverse(x) for x in re.split(self.pattern, element)]
        return '_'.join(result)

    def add_element(self, element: str):
        if element in self.forward:
            return
        self.forward[element] = str(self.index)
        self.reverse[str(self.index)] = element
        self.index += 1

    def get_forward(self, element: str):
        return self.forward[element]

    def get_reverse(self, element: str):
        return self.reverse[element]
