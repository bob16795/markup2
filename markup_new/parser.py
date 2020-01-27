from markup_new import nodes, tokenclass, output
from __main__ import *

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1 
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def devance(self, steps):
        self.tok_idx -= steps
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok


    def goto(self, to):
        self.tok_idx = to
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def body(self):
        res = ParseResult()
        node_list = []
        node = res.register(self.prop_sec())
        start = self.tok_idx
        if res.error:
            res.failure(None)
            self.goto(start)
            node = res.register(self.text_sec())
        if not res.error is None:
            return res
        while (not res.error):
            res.failure(None)
            start = self.tok_idx
            if not node is None:
                node_list.append(node)
            node = res.register(self.prop_sec())
            if res.error:
                res.failure(None)
                self.goto(start)
                node = res.register(self.text_sec())
        if self.current_tok.type == tokenclass.TT_EOF:
            res.failure(None)
        return res.success(nodes.BodyNode(node_list))

    def prop_line(self):
        start = self.tok_idx
        start_condition = self.current_tok.pos_start
        res = ParseResult()
        invert = None
        condition = None
        if self.current_tok.type == (tokenclass.TT_EXCLAIM):
            invert = True
            self.advance()
            node = self.alphanum()
            if node is None:
                return None
            condition = node.text
            if not self.current_tok.type == (tokenclass.TT_BAR):
                return None
            self.advance()
        node = self.alphanum()
        start_pos = self.current_tok.pos_start
        if node is None:
            return None
        text = node.text
        if (not (invert)) and self.current_tok.type == (tokenclass.TT_BAR):
            invert = False
            condition = text
            self.advance()
            node = self.alphanum()
            if node is None:
                return None
            prop = node.text
            if not self.current_tok.type == (tokenclass.TT_COLON):
                return None
            self.advance()
            node = self.alphanum()
            if node is None:
                return None
            value = node.text
        else:
            prop = text
            if not self.current_tok.type == (tokenclass.TT_COLON):
                return None
            self.advance()
            node = self.alphanum()
            if node is None:
                return None
            value = node.text
        if not self.current_tok.type == (tokenclass.TT_NEWLINE):
            return None
        end_pos = self.current_tok.pos_start
        self.advance()
        return nodes.PropLineNode(invert, condition, prop, value, start_condition, start_pos, end_pos)

    def prop_div(self):
        res = ParseResult()
        for i in range(3):
            tok = self.current_tok
            if not tok.type == tokenclass.TT_MINUS:
                return None
            self.advance()
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
            return None
        self.advance()
        return nodes.PropDivNode()

    def prop_sec(self):
        res = ParseResult()
        node = self.prop_div()
        if node == None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Start of Prop Section Expected"))
        node_list = []
        while node != None:
            node_list.append(node)
            node = self.prop_line()
        node = res.register(self.prop_div())
        if res.error:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "End of Prop Section Expected"))
        node_list.append(node)
        return res.success(nodes.PropSectionNode(node_list))

    def text_sec(self):
        res = ParseResult()
        node = res.register(self.text_comment())
        if res.error:
            res.failure(None)
            node = res.register(self.text_list())
        if res.error:
            res.failure(None)
            node = res.register(self.text_line())
        if res.error:
            res.failure(None)
            node = res.register(self.tag())
        if res.error:
            res.failure(None)
            node = res.register(self.text_heading())
        if res.error:
            res.failure(None)
            node = res.register(self.text_table())
        if res.error:
            return res.failure(res.error)
        node_list = []
        while not res.error:
            res.failure(None)
            node_list.append(node)
            node = res.register(self.text_comment())
            if res.error:
                res.failure(None)
                node = res.register(self.text_list())
            if res.error:
                res.failure(None)
                node = res.register(self.text_line())
            if res.error:
                res.failure(None)
                node = res.register(self.tag())
            if res.error:
                res.failure(None)
                node = res.register(self.text_heading())
            if res.error:
                res.failure(None)
                node = res.register(self.text_table())
        res.failure(None)
        node = res.register(self.text_par_end())
        if res.error:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "End of text Section Expected"))
        node_list.append(node)
        return res.success(nodes.TextSectionNode(node_list))

    def text_par_end(self):
        res = ParseResult()
        if self.current_tok.type in (tokenclass.TT_NEWLINE, tokenclass.TT_EOF):
            self.advance()
            while self.current_tok.type in (tokenclass.TT_NEWLINE):
                self.advance()
            return res.success(nodes.TextParEndNode())
        return res.failure(output.InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "End Paragraph Expected"))

    def text_line(self):
        res = ParseResult()
        text = ""
        node = self.alphanummore()
        while node is not None:
            text += node.text
            self.advance()
            node = res.register(self.alphanummore())
        res.failure(None)
        if text == "":
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no Text in line"))
        if not self.current_tok.type in (tokenclass.TT_NEWLINE, tokenclass.TT_EOF):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no end of line after text"))
        self.advance()
        return res.success(nodes.TextLineNode(text))

    def text_table(self):
        res = ParseResult()
        rows = []
        node = res.register(self.table_top())
        if res.error:
            return res.failure(res.error)
        while node is not None:
            rows.append(node)
            node = res.register(self.table_row())
        res.failure(None)
        if len(rows) < 2:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "not enough rows in table"))
        return res.success(nodes.TableNode(rows))

    def text_comment(self):
        start = self.current_tok.pos_start
        res = ParseResult()
        if not self.current_tok.type is (tokenclass.TT_EXCLAIM):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no exclaim starting comment"))
        text = ""
        self.advance()
        while not self.current_tok.type in (tokenclass.TT_NEWLINE, tokenclass.TT_EOF):
            if self.current_tok.value != None:
                text += self.current_tok.value
            elif self.current_tok.type == tokenclass.TT_COLON:
                text += ":"
            elif self.current_tok.type == tokenclass.TT_MINUS:
                text += "-"
            elif self.current_tok.type == tokenclass.TT_DOLLAR:
                text += "$"
            elif self.current_tok.type == tokenclass.TT_STAR:
                text += "*"
            elif self.current_tok.type == tokenclass.TT_EXCLAIM:
                text += "!"
            elif self.current_tok.type == tokenclass.TT_UNDERSCORE:
                text += "_"
            elif self.current_tok.type == tokenclass.TT_LPAREN:
                text += "("
            elif self.current_tok.type == tokenclass.TT_RPAREN:
                text += ")"
            self.advance()
        end = self.current_tok.pos_start
        self.advance()
        return res.success(nodes.TextCommentNode(text, start, end))

    def text_heading(self):
        res = ParseResult()
        start = self.tok_idx
        node = res.register(self.heading_3())
        if res.error:
            res.failure(None)
            self.goto(start)
            node = res.register(self.heading_2())
        if res.error:
            res.failure(None)
            self.goto(start)
            node = res.register(self.heading_1())
        if res.error:
            self.goto(start)
            return res.failure(res.error)
        return res.success(node)

    def table_top(self):
        res = ParseResult()
        heading = res.register(self.table_row())
        if res.error:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "table has no heading"))
        split = res.register(self.table_split())
        if res.error:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "table row has no split"))
        return res.success(nodes.TableHeadingNode(heading.columns))
    
    def table_row(self):
        res = ParseResult()
        start_pos = self.current_tok.pos_start
        error = False
        text = []
        while error == False:
            error = True
            if self.current_tok.type is tokenclass.TT_BAR:
                self.advance()
                node = self.alphanum()
                if not node is None:
                    text.append(node.text)
                    error = False
                else:
                    self.devance(1)
        if text == []:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "table sucks"))
        if not self.current_tok.type is tokenclass.TT_BAR:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "table row has no end"))
        self.advance()
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        end_pos = self.current_tok.pos_start
        self.advance()
        return res.success(nodes.TableRowNode(text, start_pos, end_pos))

    def table_split(self):
        res = ParseResult()
        error = False
        text = []
        while not error:
            error = True
            if self.current_tok.type is tokenclass.TT_BAR:
                self.advance()
                while self.current_tok.type is tokenclass.TT_MINUS:
                    self.advance()
                    error = False
                if error is True:
                    self.devance(1)
        if not self.current_tok.type is tokenclass.TT_BAR:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "table row has no end"))

        self.advance()
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return res.success(nodes.TableSplitNode())


    def heading_1(self):
        res = ParseResult()
        for i in range(1):
            tok = self.current_tok
            if not tok.type == tokenclass.TT_HASH:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "not enough hashes"))
            self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return nodes.Heading1Node(text)

    def heading_2(self):
        res = ParseResult()
        for i in range(2):
            tok = self.current_tok
            if not tok.type == tokenclass.TT_HASH:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "not enough hashes"))
            self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return nodes.Heading2Node(text)

    def heading_3(self):
        res = ParseResult()
        for i in range(3):
            tok = self.current_tok
            if not tok.type == tokenclass.TT_HASH:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "not enough hashes"))
            self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return nodes.Heading3Node(text)

    def tag(self):
        res = ParseResult()
        if not self.current_tok.type is (tokenclass.TT_LTAG):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no tag start"))
        self.advance()
        if not self.current_tok.type in (tokenclass.TT_TEXT, tokenclass.TT_NUM):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no tag text"))
        tag_name = self.current_tok.value
        self.advance()
        tag_value = ""
        if self.current_tok.type is (tokenclass.TT_COLON):
            self.advance()
            node = self.alphanum()
            if node is None:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no tag text"))
            tag_value = node.text
        if not self.current_tok.type is (tokenclass.TT_RTAG):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no tag end"))
        self.advance()
        if not self.current_tok.type is (tokenclass.TT_NEWLINE):
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no new line after tag"))
        self.advance()
        return res.success(nodes.TagNode(tag_name, tag_value))

    def text_list(self):
        res = ParseResult()
        node_list = []
        start = self.tok_idx
        node = None
        error = False
        while error == False:
            start = self.tok_idx
            node_list.append(node)
            node = res.register(self.list_level_3())
            if node == None:
                res.failure(None)
                self.goto(start)
                node = res.register(self.list_level_2())
            if node is None:
                res.failure(None)
                self.goto(start)
                node = res.register(self.list_level_1())
            if node == None:
                error = True
                self.goto(start)
        res.failure(None)
        if node_list == [None]:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no list elements"))
        return res.success(nodes.ListNode(node_list[1:]))

    def list_level_1(self):
        res = ParseResult()
        if not self.current_tok.type == tokenclass.TT_MINUS:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no starting dash"))
        self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        if not self.current_tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return res.success(nodes.ListLevel1Node(text))
        
    def list_level_2(self):
        res = ParseResult()
        if not self.current_tok.type == tokenclass.TT_IDENT:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no starting ident"))
        self.advance()
        res = ParseResult()
        if not self.current_tok.type == tokenclass.TT_MINUS:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no starting dash"))
        self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        if not self.current_tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return res.success(nodes.ListLevel2Node(text))
        
    def list_level_3(self):
        res = ParseResult()
        for _ in range(2):
            if not self.current_tok.type == tokenclass.TT_IDENT:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no starting ident"))
            self.advance()
        res = ParseResult()
        if not self.current_tok.type == tokenclass.TT_MINUS:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no starting dash"))
        self.advance()
        node = self.alphanummore()
        if node is None:
            return res.failure(output.InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "no text in heading"))
        text = node.text
        tok = self.current_tok
        if not tok.type == tokenclass.TT_NEWLINE:
                return res.failure(output.InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "no newline after heading"))
        self.advance()
        return res.success(nodes.ListLevel3Node(text))
        

    def alphanum(self):
        text = ""
        found = True
        start = self.tok_idx 
        while found:
            found = False
            if self.current_tok.type is tokenclass.TT_UNDERSCORE:
                found = True
                text += "_"
                self.advance()
            if self.current_tok.type is tokenclass.TT_EXCLAIM:
                found = True
                text += "!"
                self.advance()
            if self.current_tok.type is tokenclass.TT_MINUS:
                found = True
                text += "-"
                self.advance()
            if self.current_tok.type is tokenclass.TT_LPAREN:
                found = True
                text += "("
                self.advance()
            if self.current_tok.type is tokenclass.TT_RPAREN:
                found = True
                text += ")"
                self.advance()
            if self.current_tok.type is tokenclass.TT_STAR:
                found = True
                text += "*"
                self.advance()
            if self.current_tok.type is tokenclass.TT_DOLLAR:
                found = True
                text += "$"
                self.advance()
            if self.current_tok.type in (tokenclass.TT_TEXT, tokenclass.TT_NUM):
                found = True
                text += self.current_tok.value
                self.advance()
        if text == "":
            return None
        if text == "---":
            self.devance(3)
            return None
        return nodes.AlphaNumNode(text)

    def alphanummore(self):
        text = ""
        found = True
        start = self.tok_idx 
        while found:
            found = False
            if self.current_tok.type is tokenclass.TT_UNDERSCORE:
                found = True
                text += "_"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_PLUS:
                found = True
                text += "+"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_COLON:
                found = True
                text += ":"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_EXCLAIM:
                found = True
                text += "!"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_MINUS:
                found = True
                text += "-"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_LPAREN:
                found = True
                text += "("
                self.advance()
            elif self.current_tok.type is tokenclass.TT_RPAREN:
                found = True
                text += ")"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_STAR:
                found = True
                text += "*"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_DOLLAR:
                found = True
                text += "$"
                self.advance()
            elif self.current_tok.type is tokenclass.TT_LBRACKET:
                found = True
                text += "["
                self.advance()
            elif self.current_tok.type is tokenclass.TT_RBRACKET:
                found = True
                text += "]"
                self.advance()
            elif self.current_tok.type in (tokenclass.TT_TEXT, tokenclass.TT_NUM):
                found = True
                text += self.current_tok.value
                self.advance()
        if text == "":
            return None
        return nodes.AlphaNumNode(text)

    def parse(self):
        res = self.body()
        if not res.error and self.current_tok.type != tokenclass.TT_EOF:
            res.failure(output.InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected prop or text secction"))
        return res
