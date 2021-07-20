from markup_new import lexer, parser, interpreter, output
import click
import os, re
import threading
import click_completion
click_completion.init()

@click.command()
@click.argument('files', nargs=-1, required=True)
@click.option('--tree', '-t', help='prints a parser tree for the document.', is_flag=True)
@click.option('--token-tree', '-k', help='prints the tokens in the document.', is_flag=True)
@click.option('--verbose', '-v', help='Incerases the annoyingness of the compiler.', count=True, default=2)
@click.option('--quiet', '-q', help='sets verbosity to zero.', default=False, is_flag=True)
@click.option('--fullverbose', '-V', help='sets verbose to 1000.', is_flag=True, default=False)
@click.option('--force', '-f', help='ignore errors', is_flag=True, default=False)
def main(files, tree, token_tree,  verbose, quiet, fullverbose, force):
    if quiet or tree:
        verbose = 0
    if fullverbose:
        verbose = 1000
    output.LOGGING_VERBOSITY = verbose
    output.IGNORE_QUIT = force
    compile(files, tree, token_tree)

def compile(files, tree, token_tree):
    mt = multi_tasker()
    for file_name in files:
        if os.path.isfile(file_name):
            mt.add_to_queue((file_name, os.getcwd(), tree, token_tree))
        else:
            start_pos = output.Position(0, 0, 0,  "STDIN", file_name)
            end_pos = output.Position(len(file_name), 0, len(file_name), "StdIn", file_name)
            output.NoSuchPathError(start_pos, end_pos, file_name).print()
    mt.finish()

class multi_tasker():
    """
    creates compiling workers and threads them
    """

    def __init__(self):
        self.threads = list()
        self.index = 0

    def add_to_queue(self, args):
        x = threading.Thread(target=self.compile, args=args)
        self.threads.append(x)

    @staticmethod
    def compile(file_name, wd, tree=False, token_tree=False):
        from markup_new import lexer, parser, interpreter
        with open(wd + "/" + file_name, "r") as f:
            output.LexingLog(wd + "/" + file_name).print()
            tokens, error = lexer.run(f.read(), file_name)
            if tokens is None:
                error.print()

            if token_tree:
                print(tokens)
                quit()
            
            output.ParsingLog(wd + "/" + file_name).print()
            parser_obj = parser.Parser(tokens)
            ast = parser_obj.parse()

            if ast.error:
                ast.error.print()

            if tree:
                print(ast.node)
                quit()

            intrepreter_obj = interpreter.Interpreter()
            file, props = intrepreter_obj.visit(ast.node, wd=wd, file_name=file_name)

            use = props["use"]
            output_file = props["output"]
            ignore = props["ignore"]
            if ignore != "True":
                if output_file == "":
                    print(file.__str__())
                else:
                    file.finish()
                    output.WritingLog(output_file).print()
                    with open(output_file, "wb+") as out:
                        out.write(file.__str__().encode())
            if use != "":
                mt = multi_tasker()
                for pattern in use.split(";"):
                    pattern = pattern.strip(" ")
                    path = wd + "/" + "/".join(pattern.split("/")[:-1])
                    pattern = pattern.split("/")[-1]
                    files = os.listdir(path)
                    output.UsePatternLog(pattern).print()
                    for f in sorted(files):
                        if re.search(pattern.strip(" "), f):
                            output.UseFileMatchLog(f).print()
                            mt.add_to_queue((f, path, tree, token_tree))
                mt.finish()


    def finish(self):
        for index, thread in enumerate(self.threads):
            thread.start()
        for thread in self.threads:
            thread.join()
        self.threads = list()
