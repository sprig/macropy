"""Implementation and activation of a basic macro-powered REPL."""
import code
import ast

import sys

from macropy.core.macros import expand_ast, detect_macros


class MacroConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>"):
        code.InteractiveConsole.__init__(self, locals, filename)
        self.bindings = []
        self.hygienic_aliases = {}

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            code = ""
            pass

        if code is None:
            # This means it's incomplete
            return True

        try:
            tree = ast.parse(source)
            bindings, hygienic_aliases = detect_macros(tree)
            self.hygienic_aliases.update(hygienic_aliases)

            for p, names in bindings:
                __import__(p)

            self.bindings.extend([(sys.modules[p], bindings) for (p, bindings) in bindings])

            tree = expand_ast(tree, source, self.bindings, self.hygienic_aliases)

            tree = ast.Interactive(tree.body)
            code = compile(tree, filename, symbol, self.compile.compiler.flags, 1)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            # This means there's a syntax error
            return False


        self.runcode(code)
        # This means it was successfully compiled; `runcode` takes care of
        # any runtime failures
        return False

MacroConsole().interact("0=[]=====> MacroPy Enabled <=====[]=0")
