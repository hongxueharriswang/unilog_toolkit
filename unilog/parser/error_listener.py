
from antlr4.error.ErrorListener import ErrorListener
class ThrowingErrorListener(ErrorListener):
    def __init__(self): super().__init__(); self.errors=[]
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append((line,column,msg))
        raise Exception(f"Syntax error at {line}:{column}: {msg}")
