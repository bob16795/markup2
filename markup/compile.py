from markup_new import lexer, parser, interpreter
import click
import os, re

@click.command()
@click.argument('files', nargs=-1, required=True)
def main(files):
    compile(files)

def compile(files):
    for file_name in files:
        start = os.getcwd()
        with open(file_name, "r") as f:
            tokens, error = lexer.run(f.read(), file_name)
            if tokens is None:
                print(error.as_string())
                quit()

            parser_obj = parser.Parser(tokens)
            ast = parser_obj.parse()

            if ast.error:
                print(ast.error.as_string())
                quit()

            intrepreter_obj = interpreter.Interpreter()
            file, props = intrepreter_obj.visit(ast.node)

            use = props["use"]
            output = props["output"]
            ignore = props["ignore"]
            if ignore != "True":
                if output == "":
                    print(file.__str__())
                else:
                    file.finish()
                    with open(output, "w+") as out:
                        out.write(file.__str__())
            if use != "":
                use_list = []
                for pattern in use.split(";"):
                    pattern = pattern.strip(" ")
                    path = "./" + "/".join(pattern.split("/")[:-1])
                    pattern = pattern.split("/")[-1]
                    os.chdir(start)
                    os.chdir(path)
                    files = os.listdir()
                    for f in sorted(files):
                        os.chdir(start)
                        os.chdir(path)
                        if re.search(pattern.strip(" "), f):
                            print(f"use: {f}")
                            compile([f])
            os.chdir(start)
