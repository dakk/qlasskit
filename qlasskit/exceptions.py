import ast 

class NoReturnTypeException(Exception):
    def __init__(self, message):            
        super().__init__("Return type is mandatory")

class StatementNotHandledException(Exception):
    def __init__(self, message):            
        super().__init__(ast.dump(message))

class ExpressionNotHandledException(Exception):
    def __init__(self, message):            
        super().__init__(ast.dump(message))
