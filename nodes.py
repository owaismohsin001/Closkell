class NumberNode:
    def __init__(self, number, pos_start, pos_end):
        self.number = number
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.number}"

class StringNode:
    def __init__(self, string, pos_start, pos_end):
        self.string = string
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.string}"

class ListNode:
    def __init__(self, elements, isArg, pos_start, pos_end):
        self.elements = elements
        self.isArg = isArg
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return str(self.elements)

class SetNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "{"+f"{str(self.elements)}"+"}"

class MapNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return str(self.elements)

class RecordNode:
    def __init__(self, type_, elements, extension, pos_start, pos_end):
        self.type = type_
        self.extension = extension
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{str(self.elements)} inherits {self.extension}"

class RecordInstanceNode:
    def __init__(self, type_, types, elements, pos_start, pos_end):
        self.type = type_
        self.types = types
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.type}: {str(self.elements)}"

class TupleNode:
    def __init__(self, elements, pos_start, pos_end):
        self.elements = elements
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return str(self.elements)

class UnaryNode:
    def __init__(self, unary, number, pos_start, pos_end):
        self.unary = unary
        self.number = number
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.number}"

class BinOpNode:
    def __init__(self, left, op_tok, right, pos_start, pos_end):
        self.left = left
        self.op = op_tok
        self.right = right
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"({self.left}, {self.op}, {self.right})"

class FuncDefNode:
    def __init__(self, identifier, args, expr, pos_start, pos_end):
        self.identifier = identifier
        self.args = args
        self.expr = expr
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"let {self.identifier} {self.args} = {self.expr}"

class FunCallNode:
    def __init__(self, id, args, pos_start, pos_end):
        self.identifier = id
        self.args = args
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.identifier}" "{" + str(self.args) + "}"

class FuncShowNode:
    def __init__(self, id, pos_start, pos_end):
        self.identifier = id
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{self.identifier}!"

class ValNode:
    def __init__(self, identifiers, exprs, pos_start, pos_end):
        self.identifiers = identifiers
        self.exprs = exprs
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"{str(self.identifiers)} = {str(self.exprs)}"


class IfNode:
    def __init__(self, cases, else_case, pos_start, pos_end):
        self.cases = cases
        self.else_case = else_case
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"if stmnt {self.cases} else {self.else_case}"

class PatternNode:
    def __init__(self, node, vars, map_context, pos_start, pos_end):
        self.node = node
        self.vars = vars
        self.map_context = map_context
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"Pattern Match: {repr(self.node)} where {self.vars}"

class ForNode:
    def __init__(self, iterator, identifier_expr, expr, filter, pos_start, pos_end):
        self.iterator = iterator
        self.identifier_expr = identifier_expr
        self.expr = expr
        self.filter = filter
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"for {self.iterator} in {self.identifier_expr} | {self.expr}"

class WhenNode:
    def __init__(self, statement, expr, pos_start, pos_end):
        self.statement = statement
        self.expr = expr
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"when {self.statement} then {self.expr}"

class AlgebraDefNode:
    def __init__(self, identifier, cases, default, pos_start, pos_end):
        self.identifier = identifier
        self.cases = cases
        self.default = default
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"data {self.identifier} = {self.cases} else {self.default}"

class AddCaseNode:
    def __init__(self, identifier, condition, expr, pos_start, pos_end):
        self.identifier = identifier
        self.condition = condition
        self.expr = expr
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"case {self.identifier} {self.condition} -> {self.expr}"

class AddAlgebraCaseNode:
    def __init__(self, identifier, condition, expr, pos_start, pos_end):
        self.identifier = identifier
        self.condition = condition
        self.expr = expr
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"case {self.identifier} || {self.expr} -> {self.condition}"
