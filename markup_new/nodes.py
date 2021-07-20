class PropDivNode:
    def __init__(self):
        pass

    def __repr__(self):
        return f'YAML'

class PropLineNode:
    def __init__(self, invert, condition, property, value, condition_start, start_pos, end_pos):
        self.invert = invert
        self.condition = condition
        self.property = property
        self.value = value

        self.start_condition = condition_start
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return f'{self.condition.strip(" ")} == {not(self.invert)} then {self.property.strip(" ")} = {self.value.strip(" ")}'


class PropSectionNode:
    def __init__(self, nodes):
        self.nodes = nodes

    def __repr__(self):
        string = ""
        for i in self.nodes:
            string += i.__repr__()
            string += "\n"
        string += "\n"
        return string[:-1]

class TextSectionNode:
    def __init__(self, nodes):
        self.nodes = nodes

    def __repr__(self):
        string = ""
        for i in self.nodes:
            string += i.__repr__()
            string += "\n"
        return string[:-1]
       
class ListNode:
    def __init__(self, nodes):
        self.nodes = nodes

    def __repr__(self):
        string = ""
        for i in self.nodes:
            string += i.__repr__()
            string += "\n"
        return string[:-1]

class TextLineNode:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

class TextParEndNode:
    def __init__(self):
        pass

    def __repr__(self):
        return f'\n'

class TableSplitNode:
    def __init__(self, ratio):
        self.ratio = ratio
        self.total = sum(ratio)

    def __repr__(self):
        return f'-' * self.total

class TextCommentNode:
    def __init__(self, text, start_pos, end_pos):
        self.text = text
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        return "!" + self.text

class TextHeadingNode:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

class Heading1Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text + "\n" + "-" * (len(self.text) + 1)

class Heading2Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text + "\n" + "=" * (len(self.text) + 1)

class Heading3Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text + "\n" + "+" * (len(self.text) + 1)

class ListLevel1Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "-" + self.text

class ListLevel2Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "  -" + self.text

class ListLevel3Node:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "    -" + self.text

class TagNode:
    def __init__(self, name, to):
        self.name = name
        self.to = to

    def __repr__(self):
        return "TAG:" + self.name + ", TO:" + self.to

class AlphaNumNode:
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

class TableRowNode:
    def __init__(self, columns, start_pos, end_pos):
        self.columns = columns

        self.start_pos = start_pos
        self.end_pos = end_pos

    def __repr__(self):
        string = ""
        for i in self.columns:
            string += i.__repr__()
            string += "|"
        return string[:-1]

class TableNode:
    def __init__(self, heading, rows):
        self.rows = rows
        self.heading = heading
        
    def __repr__(self):
        string = ""
        for i in self.rows:
            string += i.__repr__()
            string += "\n"
        return string[:-1]

class TableHeadingNode:
    def __init__(self, columns, ratio):
        self.columns = columns
        self.ratio = ratio
        self.total = sum(ratio)

    def __repr__(self):
        string = ""
        for i in self.columns:
            string += i.__repr__()
            string += "|"
        return string[:-1]

class BodyNode:
    def __init__(self, nodes):
        self.nodes = nodes

    def __repr__(self):
        string = ""
        for i in self.nodes:
            string += i.__repr__()
            string += "\n"
        return string[:-1]
