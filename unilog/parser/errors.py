class UniLangSyntaxError(Exception):
    def __init__(self, message, line=None, column=None):
        self.line=line; self.column=column; super().__init__(message)
