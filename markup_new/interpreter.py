from pdfer import files
from markup_new import lexer, parser, errors
import os
import re

class Interpreter:
    def visit(self, node, **kwargs):
        method_name = f'Visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, **kwargs)

    def no_visit_method(self, node, **kwargs):
        raise Exception(f'No visit_{type(node).__name__} method Defined')

    def Visit_BodyNode(self, node):
        props = {"output":    "",
                 "font_face": "",
                 "use":       "",
                 "ignore":    "False",
                 "slave":     "False"}
        file = files.pdf_file()
        for i in node.nodes:
            props, file = self.visit(i, file=file, props = props)
        return file, props

    def Visit_TextSectionNode(self, node, file, props):
        text = ""
        for i in node.nodes:
            text, file = self.visit(i, file=file, props=props, text=text)
        return props, file

    def Visit_TextLineNode(self, node, file, props, text):
        line = node.text
        for key in props:
            line = line.replace("()"+key+"()", props[key])
        text += line + " "
        return text, file

    def Visit_TextParEndNode(self, node, file, props, text):
        file.add_text(text[:-1], 12)
        text = ""
        return text, file

    def Visit_Heading1Node(self, node, file, props, text):
        file.add_heading(node.text, 1)
        return text, file

    def Visit_Heading2Node(self, node, file, props, text):
        file.add_heading(node.text, 2)
        return text, file

    def Visit_Heading3Node(self, node, file, props, text):
        file.add_heading(node.text, 3)
        return text, file

    def Visit_ListLevel1Node(self, node, file, props, text):
        file.add_text("- " + node.text, 12)
        return text, file

    def Visit_ListLevel2Node(self, node, file, props, text):
        file.add_text("    - " + node.text, 12)
        return text, file

    def Visit_ListLevel3Node(self, node, file, props, text):
        file.add_text("        - " + node.text, 12)
        return text, file

    def Visit_TextCommentNode(self, node, file, props, text):
        if node.text[:4] == "Inc:":
            slave_start = props["slave"]
            props["slave"] = "True"
            start = os.getcwd()
            pattern = node.text[4:]
            pattern = pattern.strip(" ")
            path = "./" + "/".join(pattern.split("/")[:-1])
            pattern = pattern.split("/")[-1]
            os.chdir(path)
            for f in sorted(os.listdir("./")):
                os.chdir(start)
                os.chdir(path)
                if re.search(pattern, f):
                    with open(f, "r") as f:
                        tokens, error = lexer.run(f.read(), f.name)
                        if error:
                            print(error.as_string())
                            quit()

                        parser_obj = parser.Parser(tokens)
                        ast = parser_obj.parse()

                        if ast.error:
                            print(ast.error.as_string())
                            quit()
                        for i in ast.node.nodes:
                            props, file = self.visit(i, file=file, props = props)
            os.chdir(start)
            props["slave"] = slave_start
        return text, file

    def Visit_TagNode(self, node, file, props, text):
        if node.name == "COL":
            file.columns = int(node.to)
        elif node.name == "IDX":
            file.add_index_entry(node.to)
        elif node.name == "CPT":
            file.add_heading(node.to, -1)
        elif node.name == "PRT":
            file.add_heading(node.to, -2)
        return text, file

    def Visit_PropSectionNode(self, node, file, props):
        for i in node.nodes:
            prop, value = self.visit(i, props=props)
            if prop == "font_face":
                file.font_face = value
            if prop == "title":
                file.title = value
            if prop == "title_page":
                file.title_page = value
            if prop == "output":
                if not os.path.isdir("/".join(value.split("/")[:-1])):
                    print(errors.NoSuchPathError(i.start_pos, i.end_pos, "'"+ value + "'").as_string())
                    quit()
            props[prop] = value
        return props, file

    def Visit_PropDivNode(self, node, props):
        return "", ""

    def Visit_PropLineNode(self, node, props):
        if node.condition == None:
            return node.property.strip(" "), node.value.strip(" ")
        if not node.condition.strip(" ") in props:
            print(errors.NoSuchPropDefinedError(node.start_condition, node.start_pos, "'"+ node.condition.strip(" ") + "'").as_string())
            quit()
        if node.invert == (props[node.condition.strip(" ")] == "False"):
            return node.property.strip(" "), node.value.strip(" ")
        return "", None
