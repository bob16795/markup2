from pdfer import files, objects
from markup_new import lexer, parser, output
from __main__ import *
import os
import re

class Interpreter:
    def visit(self, node, **kwargs):
        method_name = f'Visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, **kwargs)

    def no_visit_method(self, node, **kwargs):
        raise Exception(f'No visit_{type(node).__name__} method Defined')

    def Visit_BodyNode(self, node, wd, file_name):
        props = {"output":    "",
                 "font_face": "",
                 "use":       "",
                 "file_name": file_name,
                 "ignore":    "False",
                 "slave":     "False"}
        file = files.pdf_file()
        for i in node.nodes:
            props, file = self.visit(i, file=file, props = props, wd = wd)
        return file, props

    def Visit_TextSectionNode(self, node, file, props, wd):
        text = ""
        for i in node.nodes:
            text, file = self.visit(i, file=file, props=props, text=text, wd = wd)
        return props, file

    def Visit_TextLineNode(self, node, file, props, text, wd):
        line = node.text
        for key in props:
            line = line.replace("()"+key+"()", props[key])
        text += line + " "
        return text, file

    def Visit_TextParEndNode(self, node, file, props, text, wd):
        file.add_text(text[:-1], 12)
        text = ""
        return text, file

    def Visit_Heading1Node(self, node, file, props, text, wd):
        file.add_heading(node.text, 1)
        return text, file

    def Visit_Heading2Node(self, node, file, props, text, wd):
        file.add_heading(node.text, 2)
        return text, file

    def Visit_Heading3Node(self, node, file, props, text, wd):
        file.add_heading(node.text, 3)
        return text, file

    def Visit_ListNode(self, node, file, props, text, wd):
        for i in node.nodes:
            file = self.visit(i, file=file, props=props)
        return text, file

    def Visit_ListLevel1Node(self, node, file, props):
        file.add_text("- " + node.text, 12)
        return file

    def Visit_ListLevel2Node(self, node, file, props):
        file.add_text("    - " + node.text, 12)
        return file

    def Visit_ListLevel3Node(self, node, file, props):
        file.add_text("        - " + node.text, 12)
        return file

    def Visit_TextCommentNode(self, node, file, props, text, wd):
        if node.type == "If":
            node_prop = node.text.split("|")[0].strip(" ")
            node_prop = node.text.split("|")[0].strip(" ")
            if type == None:
                text = "IGNORE"
        if node.type == "EndIf":
            text = ""
        if node.type == "Inc":
            slave_start = props["slave"]
            props["slave"] = "True"
            pattern = node.text
            pattern = pattern.strip(" ")
            if pattern[0] == "/":
                path = "/" + "/".join(pattern.split("/")[:-1])
            else:
                path = wd + "/" + "/".join(pattern.split("/")[:-1])
            pattern = pattern.split("/")[-1]
            add = 0
            for f in sorted(os.listdir(path)):
                if re.search(pattern, f):
                    add += 1
                    output.IncludeLog(f).print()
                    if f == props["file_name"]:
                        output.CircularRefError(node.start_pos, node.end_pos, "'" + f + "'").print()
                    with open(path + "/" +f, "r") as f:
                        tokens, error = lexer.run(f.read(), f.name)
                        if error:
                            error.print()

                        output.ParsingLog(f.name).print()
                        parser_obj = parser.Parser(tokens)
                        ast = parser_obj.parse()

                        if ast.error:
                            ast.error.print()
                        for i in ast.node.nodes:
                            props, file = self.visit(i, file=file, props = props, wd = path)
            if add == 0:
                print(warnings.NoFileIncludedWarning(node.start_pos, node.end_pos, "'"+ pattern + "@" + path + "'").as_string())
            props["slave"] = slave_start
        return text, file

    def Visit_TagNode(self, node, file, props, text, wd):
        if node.name == "COL":
            file.columns = int(node.to)
        elif node.name == "IDX":
            file.add_index_entry(node.to)
        elif node.name == "CPT":
            file.add_heading(node.to, -1)
        elif node.name == "PRT":
            file.add_heading(node.to, -2)
        return text, file

    def Visit_TableNode(self, node, file, props, text, wd):
        file, table, width = self.visit(node.rows[0], file=file)
        for row in node.rows[1:]:
            table, row_width = self.visit(row, file=file, table=table)
            if width != row_width:
                output.VaryingTableRowSizeError(row.start_pos, row.end_pos, f"{width} != {row_width}").print()
        file.add_table(table)
        return text, file

    def Visit_TableHeadingNode(self, node, file):
        file.add_space(12)
        col_size = ((file.media_box[0]-200) - (file.column_spacing * (file.columns - 1))) / file.columns
        col_x = ((col_size + file.column_spacing) * (file.current_column - 1)) + 100 
        table = objects.table_object(len(node.columns), col_size, col_x, file.y, node.columns)
        return file, table, len(node.columns)

    def Visit_TableRowNode(self, node, file, table):
        table.append(node.columns)
        return table, len(node.columns)

    def Visit_PropSectionNode(self, node, file, props, wd):
        for i in node.nodes:
            prop, value = self.visit(i, props=props)
            if prop == "font_face":
                file.font_face = value
            if prop == "title":
                file.title = value
            if prop == "title_page":
                file.title_page = (value == "True")
            if prop == "toc":
                file.include_toc = (value == "True")
            if prop == "index":
                file.include_index = (value == "True")
            if prop == "output":
                path = wd  + "/" + "/".join(value.split("/")[:-1])
                if path and not os.path.isdir(path):
                    output.NoSuchPathError(i.start_pos, i.end_pos, "'"+ path + "'").print()
                value = path + "/" + value.split("/")[-1]
            props[prop] = value
        return props, file

    def Visit_PropDivNode(self, node, props):
        return "", ""

    def Visit_PropLineNode(self, node, props):
        if node.condition == None:
            return node.property.strip(" "), node.value.strip(" ")
        if not node.condition.strip(" ") in props:
            print(output.NoSuchPropDefinedError(node.start_condition, node.start_pos, "'"+ node.condition.strip(" ") + "'").as_string())
            quit()
        if node.invert == (props[node.condition.strip(" ")] == "False"):
            return node.property.strip(" "), node.value.strip(" ")
        return "", None
