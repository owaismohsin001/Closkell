from tokens import *
from errors import InvalidSyntaxError
from results import ParseResult
from nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.next_tok_idx = 0
        self.advance()

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx<len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        if self.next_tok_idx >= 0 and self.next_tok_idx<len(self.tokens):
            self.next_tok = self.tokens[self.next_tok_idx]

    def advance(self):
        self.tok_idx += 1
        self.next_tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Expecte '+', '-', '*' or, '/'"
			))
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()
        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
        statement = res.register(self.statement())
        if res.error: return res
        statements.append(statement)
        more_statements = True
        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements: break
            statement = res.try_register(self.statement())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(ListNode(
            statements,
            False,
            pos_start,
            self.current_tok.pos_end.copy()
        ))

    def statement(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.matches(TT_KEYWORD, "let"):
            self.advance()
            identifier = self.current_tok
            self.advance()
            args = []
            while self.current_tok.type == TT_IDENTIFIER:
                args.append(self.current_tok)
                self.advance()
            if self.current_tok.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
            	   pos_start, self.current_tok.pos_end.copy(),
        		   "Expected '='"
                ))
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(FuncDefNode(identifier, args, expr, pos_start, self.current_tok.pos_end.copy()))
        elif self.current_tok.matches(TT_KEYWORD, "val"):
            identifiers = []
            exprs = []
            vars = []
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
            	   pos_start, self.current_tok.pos_end.copy(),
        		   "Expected IDENTIFIER"
                ))
            identifiers.append(self.current_tok)
            res.register_advancement()
            self.advance()
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(InvalidSyntaxError(
                	   pos_start, self.current_tok.pos_end.copy(),
            		   "Expected IDENTIFIER"
                    ))
                identifiers.append(self.current_tok)
                res.register_advancement()
                self.advance()
            if self.current_tok.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
            	   pos_start, self.current_tok.pos_end.copy(),
        		   "Expected '='"
                ))
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            exprs.append(expr)
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                exprs.append(expr)
            return res.success(ValNode(identifiers, exprs, pos_start, self.current_tok.pos_end.copy()))
        elif self.current_tok.matches(TT_KEYWORD, "class"):
            expr = res.register(self.case_class())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "case"):
            expr = res.register(self.add_case())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "data"):
            expr = res.register(self.algebraic_data())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "curry"):
            expr = res.register(self.curry_function())
            if res.error: return res
            return res.success(expr)
        expr = res.register(self.expr())
        if res.error: return res
        return res.success(expr)

    def case_class(self):
        res = ParseResult()
        identifier = None
        body = None
        vars = []
        args = []
        map_pos = None
        map_context = None
        pos_start = self.current_tok.pos_start
        if not self.current_tok.matches(TT_KEYWORD, "class"):
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected 'class'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected IDENTIFIER"
            ))
        identifier = self.current_tok
        res.register_advancement()
        self.advance()
        while self.current_tok.type == TT_IDENTIFIER:
            args.append(self.current_tok)
            res.register_advancement()
            self.advance()
        body = IfNode([], FunCallNode(Token(TT_IDENTIFIER, "null"), [], pos_start, self.current_tok.pos_end), pos_start, self.current_tok.pos_end.copy())
        if self.current_tok.matches(TT_KEYWORD, "where"):
            identifiers = []
            exprs = []
            res.register_advancement()
            self.advance()
            i = 0
            if self.current_tok.type == TT_RCURLY:
                res.register_advancement()
                self.advance()
                map_pos = i
                if self.current_tok.type != TT_LCURLY:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected '}'"
                    ))
                res.register_advancement()
                self.advance()
            elif self.current_tok.type == TT_IDENTIFIER:
                identifiers.append(self.current_tok)
                res.register_advancement()
                self.advance()
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected IDENTIFIER or '{'"
                ))
            i += 1
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type == TT_RCURLY:
                    res.register_advancement()
                    self.advance()
                    map_pos = i
                    res.register_advancement()
                    self.advance()
                else:
                    identifiers.append(self.current_tok)
                    res.register_advancement()
                    self.advance()
                i+=1
            if self.current_tok.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            i = 0
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if i == map_pos:
                map_context = expr
            else:
                expr = exprs.append(expr)
            i += 1
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                if i == map_pos:
                    map_context = expr
                else:
                    expr = exprs.append(expr)
                i+=1
            if len(identifiers) != len(exprs):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "IDENTIFIERS and expression are unequal"
                ))
            vars = list(zip(identifiers, exprs))
        body = PatternNode(body, vars, map_context, pos_start, self.current_tok.pos_end.copy())
        return res.success(FuncDefNode(identifier, args, body, pos_start, self.current_tok.pos_end.copy()))

    def add_case(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        identifier = None
        condition = None
        expr = None
        if not self.current_tok.matches(TT_KEYWORD, "case"):
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected 'case'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected IDENTIFIER"
            ))
        identifier = FuncShowNode(self.current_tok, self.current_tok.pos_start, self.current_tok.pos_end)
        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_DATAOR:
            res.register_advancement()
            self.advance()
            record = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_SARROW:
                res.register_advancement()
                self.advance()
                condition = res.register(self.expr())
                if res.error: return res
            else:
                condition = FunCallNode(Token(TT_IDENTIFIER, "true"), [], self.current_tok.pos_start.copy(), self.current_tok.pos_end.copy())
            return res.success(AddAlgebraCaseNode(identifier, condition if condition else None, record, pos_start, self.current_tok.pos_end.copy()))
        if self.current_tok.matches(TT_KEYWORD, "default"):
            res.register_advancement()
            self.advance()
        else:
            condition = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type != TT_SARROW:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected '->'"
            ))
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res
        return res.success(AddCaseNode(identifier, condition if condition else None, expr, pos_start, self.current_tok.pos_end.copy()))

    def curry_function(self):
        res = ParseResult()
        identifier = None
        function = FuncDefNode(None, [], None, self.current_tok.pos_start, self.current_tok.pos_end)
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, "curry"):
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected 'curry'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected IDENTIFIER"
            ))
        function.identifier = self.current_tok
        res.register_advancement()
        self.advance()
        fun_expr = function
        while self.current_tok.type == TT_IDENTIFIER:
            fun_expr.expr = FuncDefNode(None, [self.current_tok], None, self.current_tok.pos_start, self.current_tok.pos_end)
            fun_expr = fun_expr.expr
            res.register_advancement()
            self.advance()
        if self.current_tok.type != TT_EQUALS:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected '='"
            ))
        res.register_advancement()
        self.advance()
        last_expr = res.register(self.expr())
        fun_expr.expr = last_expr
        if res.error: return res
        return res.success(function)


    def algebraic_data(self):
        res = ParseResult()
        parent = None
        functions = []
        default = None
        pos_start = self.current_tok.pos_start.copy()
        def parse_true(pos_start, pos_end):
            return FunCallNode(Token(TT_IDENTIFIER, "true"), [], pos_start, pos_end)
        if not self.current_tok.matches(TT_KEYWORD, "data"):
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected 'case'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected IDENTIFIER"
            ))
        parent = RecordNode(self.current_tok, [], None, None, pos_start, self.current_tok.pos_end.copy())
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_EQUALS:
            return res.failure(InvalidSyntaxError(
        	   pos_start, self.current_tok.pos_end.copy(),
               "Expected '='"
            ))
        res.register_advancement()
        self.advance()
        record = res.register(self.expr())
        if res.error: return res
        record.extension = FuncShowNode(parent.type, pos_start, self.current_tok.pos_end.copy())
        if self.current_tok.type == TT_SARROW:
            res.register_advancement()
            self.advance()
            condition = res.register(self.expr())
            functions.append((condition, record))
        else:
            functions.append((parse_true(self.current_tok.pos_start, self.current_tok.pos_end), record))
        while self.current_tok.type == TT_DATAOR:
            res.register_advancement()
            self.advance()
            if self.current_tok.matches(TT_KEYWORD, "default"):
                res.register_advancement()
                self.advance()
                record = res.register(self.expr())
                if res.error: return res
                record.extension = FuncShowNode(parent.type, pos_start, self.current_tok.pos_end.copy())
                default = record
            else:
                record = res.register(self.expr())
                if res.error: return res
                record.extension = FuncShowNode(parent.type, pos_start, self.current_tok.pos_end.copy())
                if self.current_tok.type == TT_SARROW:
                    res.register_advancement()
                    self.advance()
                    condition = res.register(self.expr())
                    functions.append((condition, record))
                else:
                    functions.append((parse_true(self.current_tok.pos_start, self.current_tok.pos_end), record))
        return res.success(AlgebraDefNode(parent, functions, default, pos_start, self.current_tok.pos_end.copy()))

    def bin_op(self, left_fun, toks, right_fun):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        left = res.register(left_fun())
        if res.error: return res
        while (self.current_tok.type in toks) or ((self.current_tok.type, self.current_tok.value) in toks):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(right_fun())
            if res.error: return res
            left = BinOpNode(left, op_tok, right, pos_start, self.current_tok.pos_end)
        return res.success(left)

    def expr(self):
        res = ParseResult()
        binary_operation = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, "and"), (TT_KEYWORD, "or")), self.comp_expr))
        if res.error: return res
        if self.current_tok.type == TT_COLON:
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TT_LPAREN:
                res.register_advancement()
                self.advance()
                funcall = FunCallNode(binary_operation, [], binary_operation.pos_start.copy(), self.current_tok.pos_end.copy())
                return res.success(funcall)
            expr = res.register(self.expr())
            if res.error: return res
            funcall = FunCallNode(binary_operation, [expr], binary_operation.pos_start.copy(), self.current_tok.pos_end.copy())
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                funcall = FunCallNode(funcall, [expr], binary_operation.pos_start.copy(), self.current_tok.pos_end.copy())
            return res.success(funcall)
        return res.success(binary_operation)

    def comp_expr(self):
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.matches(TT_KEYWORD, "not"):
            unary_tok = self.current_tok
            res.register_advancement()
            self.advance()
            comp_expr = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryNode(unary_tok, comp_expr, pos_start, self.current_tok.pos_end.copy()))
        binary_operation = res.register(self.bin_op(self.pipeline_expr, (TT_EE, TT_NE, TT_GT, TT_GTE, TT_LT, TT_LTE, TT_DCOLON), self.pipeline_expr))
        if res.error: return res
        return res.success(binary_operation)

    def pipeline_expr(self):
        res = ParseResult()
        binary_operation = res.register(self.bin_op(self.arith_expr, (TT_PIPELINE, ), self.arith_expr))
        if res.error: return res
        return res.success(binary_operation)

    def arith_expr(self):
        res = ParseResult()
        binary_operation = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS), self.term))
        if res.error: return res
        return res.success(binary_operation)

    def term(self):
        res = ParseResult()
        binary_operation = res.register(self.bin_op(self.factor, (TT_DIV, TT_MUL, TT_INFIX), self.factor))
        if res.error: return res
        return res.success(binary_operation)

    def factor(self):
        res = ParseResult()
        binary_operation = res.register(self.bin_op(self.atom, (TT_DARROW, ), self.atom))
        if res.error: return res
        return res.success(binary_operation)

    def atom(self):
        atoms = [TT_FLOAT, TT_INT, TT_STRING, TT_IDENTIFIER, TT_RPAREN, TT_RCURLY, TT_RSQUARE, TT_ARGPOW, (TT_KEYWORD, "if")]
        res = ParseResult()
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.type in (TT_PLUS, TT_MINUS, TT_ARGPOW, TT_DCOLON):
            unary_tok = self.current_tok
            res.register_advancement()
            self.advance()
            expr = res.register(self.atom())
            if res.error: return res
            return res.success(UnaryNode(unary_tok, expr, pos_start, self.current_tok.pos_end.copy()))
        elif (self.current_tok.type == TT_FLOAT) or (self.current_tok.type == TT_INT):
            pos_end = self.current_tok.pos_end.copy()
            value = self.current_tok
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(int(value.value) if value.type == TT_INT else float(value.value), pos_start, pos_end))
        elif self.current_tok.type == TT_STRING:
            pos_end = self.current_tok.pos_end.copy()
            value = self.current_tok.value
            res.register_advancement()
            self.advance()
            return res.success(StringNode(value, pos_start, pos_end))
        elif ((self.current_tok.type == TT_IDENTIFIER) and (self.next_tok.type == TT_RCURLY)) or ((self.current_tok.type == TT_LAMBDA) and (self.next_tok.type == TT_RCURLY)):
            expr = res.register(self.record_expr())
            if res.error: return res
            return res.success(expr)
        elif (self.current_tok.type == TT_IDENTIFIER) or (self.current_tok.type == TT_EXCL):
            if self.current_tok.type == TT_EXCL:
                self.advance()
                id = res.register(self.atom())
                if res.error: return res
            else:
                id = self.current_tok
                self.advance()
            if self.current_tok.type == TT_EXCL:
                self.advance()
                return res.success(FuncShowNode(id, pos_start, self.current_tok.pos_end))
            args = []
            while (self.current_tok.type in atoms) or ((self.current_tok.type, self.current_tok.value) in atoms):
                expr = res.register(self.expr())
                if res.error: return res
                args.append(expr)
            return res.success(FunCallNode(id, args, pos_start, self.current_tok.pos_end))
        elif self.current_tok.type == TT_RPAREN:
            exprs = []
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TT_LPAREN:
                res.register_advancement()
                self.advance()
                return res.success(TupleNode(tuple(exprs), pos_start, self.current_tok.pos_end.copy()))
            expr = res.register(self.expr())
            if res.error: return res
            exprs.append(expr)
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                exprs.append(res.register(self.expr()))
                if res.error: return res
            if self.current_tok.type != TT_LPAREN:
                return res.failure(InvalidSyntaxError(
    				pos_start, self.current_tok.pos_end.copy(),
    				"Expecte ')'"
    			))
            res.register_advancement()
            self.advance()
            return res.success(exprs[0] if len(exprs) == 1 else TupleNode(tuple(exprs), pos_start, self.current_tok.pos_end.copy()))
        elif self.current_tok.type == TT_LAMBDA:
            self.advance()
            args = []
            while self.current_tok.type == TT_IDENTIFIER:
                args.append(self.current_tok)
                self.advance()
            if self.current_tok.type != TT_SARROW:
                return res.failure(InvalidSyntaxError(
            	   pos_start, self.current_tok.pos_end.copy(),
        		   "Expected '\\'"
                ))
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(FuncDefNode(None, args, expr, pos_start, self.current_tok.pos_end.copy()))
        elif self.current_tok.matches(TT_KEYWORD, "if"):
            expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(expr)
        elif (self.current_tok.type == TT_RSQUARE) or (self.current_tok.type == TT_ARGPOW and self.next_tok.type == TT_RSQUARE):
            expr = res.register(self.list_expr())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.type == TT_RCURLY:
            expr = res.register(self.map_expr())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.type == TT_HASH:
            expr = res.register(self.set_expr())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "case"):
            expr = res.register(self.case_match())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "when"):
            expr = res.register(self.when_expr())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.type == TT_PATTERN:
            expr = res.register(self.pattern_match())
            if res.error: return res
            return res.success(expr)
        elif self.current_tok.matches(TT_KEYWORD, "seq"):
            expr = res.register(self.seq_expr())
            if res.error: return res
            return res.success(expr)
        return res.failure(InvalidSyntaxError(
    	   pos_start, self.current_tok.pos_end.copy(),
		   "Expecte NUMBER, IDENTIFIER, if, or '('"
        ))

    def when_expr(self):
        res = ParseResult()
        statement = None
        expr = None
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, 'when'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'when'"
            ))
        res.register_advancement()
        self.advance()
        statement = res.register(self.statement())
        if res.error: return res
        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'then'"
            ))
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res
        return res.success(WhenNode(statement, expr, pos_start, self.current_tok.pos_end.copy()))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, 'if'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'if'"
            ))
        res.register_advancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error: return res
        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'then'"
            ))
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res
        cases.append((condition, expr))
        while self.current_tok.matches(TT_KEYWORD, 'elif'):
            res.register_advancement()
            self.advance()
            condition = res.register(self.expr())
            if res.error: return res
            if not self.current_tok.matches(TT_KEYWORD, 'then'):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'then'"
                ))
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            cases.append((condition, expr))
        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            else_case = res.register(self.expr())
        return res.success(IfNode(cases, else_case, pos_start, self.current_tok.pos_end.copy()))

    def for_expr(self):
        res = ParseResult()
        filter = None
        iterator = None
        identifier_expr = None
        expr = None
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, "for"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'for'"
            ))
        res.register_advancement()
        self.advance()
        iterator = self.current_tok
        res.register_advancement()
        self.advance()
        if not self.current_tok.matches(TT_KEYWORD, "in"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'in'"
            ))
        res.register_advancement()
        self.advance()
        identifier_expr = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type != TT_PATTERN:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '|'"
            ))
        res.register_advancement()
        self.advance()
        expr = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type == TT_SARROW:
            res.register_advancement()
            self.advance()
            if not self.current_tok.matches(TT_KEYWORD, "if"):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'if'"
                ))
            res.register_advancement()
            self.advance()
            filter = res.register(self.expr())
            if res.error: return res
        return res.success(ForNode(iterator, identifier_expr, expr, filter, pos_start, self.current_tok.pos_end.copy()))


    def map_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_LCURLY:
            res.register_advancement()
            self.advance()
            return res.success(MapNode(elements, pos_start, self.current_tok.pos_end.copy()))
        if (self.current_tok.type != TT_STRING) and (self.current_tok.type != TT_INT):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected INTEGER or STRING"
            ))
        key = res.register(self.atom())
        if res.error: return res
        if self.current_tok.type != TT_COLON:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ':'"
            ))
        res.register_advancement()
        self.advance()
        value = res.register(self.expr())
        if res.error: return res
        elements.append((key, value))
        while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()
            if (self.current_tok.type != TT_STRING) and (self.current_tok.type != TT_INT):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected INTEGER or STRING"
                ))
            key = res.register(self.atom())
            if res.error: return res
            if self.current_tok.type != TT_COLON:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ':'"
                ))
            res.register_advancement()
            self.advance()
            value = res.register(self.expr())
            if res.error: return res
            elements.append((key, value))
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))
        res.register_advancement()
        self.advance()
        return res.success(MapNode(elements, pos_start, self.current_tok.pos_end.copy()))

    def record_expr(self):
        res = ParseResult()
        elements = []
        record_type = Token(TT_IDENTIFIER, "anonymous")
        extension = None
        when_stmnt = None
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.type == TT_IDENTIFIER:
            record_type = self.current_tok
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_LCURLY:
            res.register_advancement()
            self.advance()
        else:
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected IDENTIFIER"
                ))
            identifier = self.current_tok
            elements.append(identifier)
            res.register_advancement()
            self.advance()
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                identifier = self.current_tok
                elements.append(identifier)
                res.register_advancement()
                self.advance()
            if self.current_tok.type != TT_LCURLY:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '}'"
                ))
            res.register_advancement()
            self.advance()
        if self.current_tok.matches(TT_KEYWORD, "when"):
            res.register_advancement()
            self.advance()
            when_stmnt = res.register(self.statement())
            if res.error: return res
        if self.current_tok.matches(TT_KEYWORD, "inherits"):
            res.register_advancement()
            self.advance()
            extension = res.register(self.expr())
            if res.error: return res
        return res.success(RecordNode(record_type, elements, when_stmnt, extension, pos_start, self.current_tok.pos_end.copy()))

    def set_expr(self):
        res = ParseResult()
        elements = []
        pos_start = self.current_tok.pos_start.copy()
        if self.current_tok.type != TT_HASH:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '[' or '^'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type != TT_RCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '{'"
            ))
        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_LCURLY:
            res.register_advancement()
            self.advance()
            return res.success(SetNode(elements, pos_start, self.current_tok.pos_end.copy()))
        expr = res.register(self.for_expr() if self.current_tok.matches(TT_KEYWORD, "for") else self.expr())
        if res.error: return res
        elements.append(expr)
        while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()
            expr = res.register(self.for_expr() if self.current_tok.matches(TT_KEYWORD, "for") else self.expr())
            if res.error: return res
            elements.append(expr)
        if self.current_tok.type != TT_LCURLY:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '}'"
            ))
        res.register_advancement()
        self.advance()
        return res.success(SetNode(elements, pos_start, self.current_tok.pos_end.copy()))

    def list_expr(self):
        res = ParseResult()
        elements = []
        isArg = self.current_tok.type == TT_ARGPOW
        pos_start = self.current_tok.pos_start.copy()
        if (self.current_tok.type != TT_RSQUARE) and (self.current_tok.type != TT_ARGPOW):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '[' or '^'"
            ))
        res.register_advancement()
        self.advance()
        if isArg:
            res.register_advancement()
            self.advance()
        if self.current_tok.type == TT_LSQUARE:
            res.register_advancement()
            self.advance()
            return res.success(ListNode(elements, isArg, pos_start, self.current_tok.pos_end.copy()))
        expr = res.register(self.for_expr() if self.current_tok.matches(TT_KEYWORD, "for") else self.expr())
        if res.error: return res
        elements.append(expr)
        while self.current_tok.type == TT_COMMA:
            res.register_advancement()
            self.advance()
            expr = res.register(self.for_expr() if self.current_tok.matches(TT_KEYWORD, "for") else self.expr())
            if res.error: return res
            elements.append(expr)
        if self.current_tok.type != TT_LSQUARE:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected ']'"
            ))
        res.register_advancement()
        self.advance()
        return res.success(ListNode(elements, isArg, pos_start, self.current_tok.pos_end.copy()))

    def pattern_match(self):
        res = ParseResult()
        cases = []
        else_case = None
        identifiers = []
        exprs = []
        vars = []
        map_context = None
        map_pos = None
        pos_start = self.current_tok.pos_start.copy()
        while self.current_tok.type == TT_PATTERN:
            res.register_advancement()
            self.advance()
            condition = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_SARROW:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                cases.append((condition, expr))
            else:
                else_case = condition
        ifstatement = IfNode(cases, else_case, pos_start, self.current_tok.pos_end.copy())
        if self.current_tok.matches(TT_KEYWORD, "where"):
            res.register_advancement()
            self.advance()
            i = 0
            if self.current_tok.type == TT_RCURLY:
                res.register_advancement()
                self.advance()
                map_pos = i
                if self.current_tok.type != TT_LCURLY:
                    return res.failure(InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected '}'"
                    ))
                res.register_advancement()
                self.advance()
            elif self.current_tok.type == TT_IDENTIFIER:
                identifiers.append(self.current_tok)
                res.register_advancement()
                self.advance()
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected IDENTIFIER or '{'"
                ))
            i += 1
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                if self.current_tok.type == TT_RCURLY:
                    res.register_advancement()
                    self.advance()
                    map_pos = i
                    res.register_advancement()
                    self.advance()
                else:
                    identifiers.append(self.current_tok)
                    res.register_advancement()
                    self.advance()
                i+=1
            if self.current_tok.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            i = 0
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if i == map_pos:
                map_context = expr
            else:
                expr = exprs.append(expr)
            i += 1
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                if i == map_pos:
                    map_context = expr
                else:
                    expr = exprs.append(expr)
                i+=1
            if len(identifiers) != len(exprs):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "IDENTIFIERS and expression are unequal"
                ))
            vars = list(zip(identifiers, exprs))
        return res.success(PatternNode(ifstatement, vars, map_context, pos_start, self.current_tok.pos_end.copy()))

    def case_match(self):
        res = ParseResult()
        cases = []
        else_case = None
        identifiers = []
        exprs = []
        vars = []
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, "case"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'case'"
            ))
        res.register_advancement()
        self.advance()
        first_value = res.register(self.expr())
        if res.error: return res
        if self.current_tok.type != TT_SARROW:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected '->'"
            ))
        res.register_advancement()
        self.advance()
        while self.current_tok.type == TT_PATTERN:
            res.register_advancement()
            self.advance()
            condition = res.register(self.expr())
            if res.error: return res
            condition = BinOpNode(first_value, Token(TT_EE), condition, first_value.pos_start, condition.pos_end)
            if self.current_tok.type == TT_SARROW:
                res.register_advancement()
                self.advance()
                expr = res.register(self.expr())
                if res.error: return res
                cases.append((condition, expr))
            else:
                else_case = condition.right
        ifstatement = IfNode(cases, else_case, pos_start, self.current_tok.pos_end.copy())
        if self.current_tok.matches(TT_KEYWORD, "where"):
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected IDENTIFIER"
                ))
            identifiers.append(self.current_tok)
            res.register_advancement()
            self.advance()
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                identifiers.append(self.current_tok)
                res.register_advancement()
                self.advance()
            if self.current_tok.type != TT_EQUALS:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '='"
                ))
            res.register_advancement()
            self.advance()
            expr = exprs.append(res.register(self.expr()))
            if res.error: return res
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                expr = exprs.append(res.register(self.expr()))
                if res.error: return res
            if len(identifiers) != len(exprs):
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "IDENTIFIERS and expression are unequal"
                ))
            vars = list(zip(identifiers, exprs))
        return res.success(PatternNode(ifstatement, vars, None, pos_start, self.current_tok.pos_end.copy()))

    def seq_expr(self):
        res = ParseResult()
        function = None
        when_node = None
        pos_start = self.current_tok.pos_start.copy()
        if not self.current_tok.matches(TT_KEYWORD, "seq"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'seq'"
            ))
        res.register_advancement()
        self.advance()
        statements_node = res.register(self.statements())
        statements = statements_node.elements
        if res.error: return res
        if not self.current_tok.matches(TT_KEYWORD, "end"):
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'end'"
            ))
        res.register_advancement()
        self.advance()
        if len(statements) < 2:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected at least two instructions in 'seq' block"
            ))
        when_node = WhenNode(statements[0], None, pos_start, self.current_tok.pos_end)
        when_expr = when_node
        for statement in statements[1:-1]:
            when_expr.expr = WhenNode(statement, None, pos_start, self.current_tok.pos_end)
            when_expr = when_expr.expr
        when_expr.expr = statements[-1]
        return res.success(when_node)
