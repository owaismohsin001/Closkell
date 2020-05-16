from errors import ExpectedCharError
from tokens import *

#Position
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#Lexer
class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, self.fn, self.text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_number(self):
        number_str = ""
        pos_start = self.pos.copy()
        e_count = 0
        dot_count = 0
        while (self.current_char != None) and (self.current_char in DIGITS+"."+"e"):
            if self.current_char == ".": dot_count+=1
            if self.current_char == "e": e_count+=1
            if dot_count == 2: break
            if e_count == 2: break
            if (dot_count == 1) and (e_count == 1): break
            number_str += self.current_char
            self.advance()
        if (dot_count != 0) or (e_count != 0):
            return Token(TT_FLOAT, float(number_str), pos_start, self.pos)
        else:
            return Token(TT_INT, int(number_str), pos_start, self.pos)

    def make_identifier(self):
        id_str = ""
        pos_start = self.pos.copy()
        while (self.current_char != None) and (self.current_char in LETTERS+"_"+DIGITS):
            id_str += self.current_char
            self.advance()
        return Token(TT_KEYWORD if id_str in KEYWORDS else TT_IDENTIFIER, id_str, pos_start, self.pos)

    def make_gt_or_gte(self):
        pos_start = self.pos.copy()
        tok_type = TT_GT
        self.advance()
        if self.current_char == "=":
            tok_type = TT_GTE
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_colon_or_docoln(self):
        pos_start = self.pos.copy()
        tok_type = TT_COLON
        self.advance()
        if self.current_char == ":":
            tok_type = TT_DCOLON
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_lt_or_lte(self):
        pos_start = self.pos.copy()
        tok_type = TT_LT
        self.advance()
        if self.current_char == "=":
            tok_type = TT_LTE
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_equals_or_ee_or_darrow(self):
        pos_start = self.pos.copy()
        tok_type = TT_EQUALS
        self.advance()
        if self.current_char == "=":
            tok_type = TT_EE
            self.advance()
        elif self.current_char == ">":
            tok_type = TT_DARROW
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_ne_or_excl(self):
        tok_type = TT_EXCL
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == "=":
            tok_type = TT_NE
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy()), None

    def make_infix(self):
        id_str = ''
        pos_start = self.pos.copy()
        self.advance()
        while (self.current_char != None) and (self.current_char in LETTERS+"_"+DIGITS) and (self.current_char != '`'):
            id_str += self.current_char
            self.advance()
        if self.current_char != '`':
            return None, ExpectedCharError(pos_start, self.pos, "Unexpected Character in infix identifier")
        self.advance()
        return Token(TT_INFIX, id_str, pos_start, self.pos.copy()), None

    def make_string(self):
        string = ""
        escape_character = False
        escape_characters = {
            't': '\t',
            'n': '\n'
        }
        pos_start = self.pos.copy()
        self.advance()
        while self.current_char != '"' or escape_character:
            if escape_character:
                string += escape_characters.get(self.current_char, self.current_char)
                escape_character = False
            else:
                if self.current_char == '\\':
                    escape_character = True
                else:
                    string += self.current_char
            self.advance()
        self.advance()
        return Token(TT_STRING, string, pos_start=pos_start, pos_end=self.pos.copy())

    def make_pipeline_or_pattern_or_dataor(self):
        tok_type = TT_PATTERN
        pos_start = self.pos.copy()
        self.advance()
        if self.current_char == ">":
            tok_type = TT_PIPELINE
            self.advance()
        if self.current_char == "|":
            tok_type = TT_DATAOR
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def make_sarrow_or_minus(self):
        pos_start = self.pos.copy()
        tok_type = TT_MINUS
        self.advance()
        if self.current_char == ">":
            tok_type = TT_SARROW
            self.advance()
        return Token(tok_type, pos_start=pos_start, pos_end=self.pos.copy())

    def skip_comment(self):
        self.advance()
        while not self.current_char == '\n':
            self.advance()
        self.advance()
        return

    def generate_tokens(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in '\t ':
                self.advance()
            elif self.current_char in '$':
                self.skip_comment()
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start=self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(self.make_sarrow_or_minus())
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start=self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start=self.pos))
                self.advance()
            elif self.current_char == '|':
                tokens.append(self.make_pipeline_or_pattern_or_dataor())
            elif self.current_char == '(':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == '[':
                tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == ']':
                tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '{':
                tokens.append(Token(TT_RCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == '}':
                tokens.append(Token(TT_LCURLY, pos_start=self.pos))
                self.advance()
            elif self.current_char == '#':
                tokens.append(Token(TT_HASH, pos_start=self.pos))
                self.advance()
            elif self.current_char == ',':
                tokens.append(Token(TT_COMMA, pos_start=self.pos))
                self.advance()
            elif self.current_char == ':':
                tokens.append(self.make_colon_or_docoln())
            elif self.current_char == '^':
                tokens.append(Token(TT_ARGPOW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '=':
                tokens.append(self.make_equals_or_ee_or_darrow())
            elif self.current_char == '!':
                token, error = self.make_ne_or_excl()
                if error: return [], error
                tokens.append(token)
            elif self.current_char == '"':
                tokens.append(self.make_string())
            elif self.current_char == '>':
                tokens.append(self.make_gt_or_gte())
            elif self.current_char == '<':
                tokens.append(self.make_lt_or_lte())
            elif self.current_char == '.':
                tokens.append(Token(TT_NEWLINE, pos_start=self.pos))
                self.advance()
            elif self.current_char == '\\':
                tokens.append(Token(TT_LAMBDA, pos_start=self.pos))
                self.advance()
            elif self.current_char in '`':
                tok, error = self.make_infix()
                if error: return [], error
                tokens.append(tok)
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharacterError(pos_start, self.pos, f"'{char}'")
        tokens.append(Token(TT_EOF, pos_start = self.pos))
        return tokens, None
