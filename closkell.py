from errors import RTError
from lexer import Lexer
from parser_ import Parser
from copy import deepcopy
from results import RTResult
from tokens import *
from nodes import *

class Value:
    def __init__(self):
        self.value = None
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context=None):
        self.context = context
        return self

    def added_to(self, other):
        return None, self.IllegalOperationError(other)

    def subbed_by(self, other):
        return None, self.IllegalOperationError(other)

    def multed_by(self, other):
        return None, self.IllegalOperationError(other)

    def dived_by(self, other):
        return None, self.IllegalOperationError(other)

    def lt(self, other):
        return None, self.IllegalOperationError(other)

    def lte(self, other):
        return None, self.IllegalOperationError(other)

    def gt(self, other):
        return None, self.IllegalOperationError(other)

    def gte(self, other):
        return None, self.IllegalOperationError(other)

    def ee(self, other):
        return None, self.IllegalOperationError(other)

    def ne(self, other):
        return None, self.IllegalOperationError(other)

    def execute(self, args):
        return None, self.IllegalOperationError()

    def argpowed(self):
        return None, self.IllegalOperationError()

    def instance_return(self, other):
        predefined = self.predefined[other.value]
        if (isinstance(predefined, int) or isinstance(predefined, float)):
            return Number(predefined)
        elif isinstance(predefined, str):
            return String(predefined)
        else:
            return predefined.copy()

    def get_property(self, other):
        if isinstance(other, Token) and other.type == TT_IDENTIFIER:
            if other.value in self.predefined:
                return self.instance_return(other), None
            else:
                return null, None
        else:
            if other.value in self.predefined:
                return self.instance_return(other), None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    f"{type(self).__name__} has no Property named {other.value}"
                )

    def copy(self):
        raise Exception("No copy method defined")

    def IllegalOperationError(self, other=None):
        if not other: other = self
        return RTError(
            self.pos_start, self.pos_end,
            self.context,
            'Illegal Operation'
        )

class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.predefined = {
            "type": "Number",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(
                    self.pos_start, other.pos_end,
                    self.context,
                    "Division by Zero"
                )
            return Number(self.value / other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def lt(self, other):
        if isinstance(other, Number):
            return Bool(self.value < other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def lte(self, other):
        if isinstance(other, Number):
            return Bool(self.value <= other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def gt(self, other):
        if isinstance(other, Number):
            return Bool(self.value > other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def gte(self, other):
        if isinstance(other, Number):
            return Bool(self.value >= other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def ee(self, other):
        if isinstance(other, Number):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, Number):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(1), None

    def is_true(self):
        return self.value != 0

    def is_type(self, other):
        return Bool(int(other.value == "Number")), None

    def notted(self):
        return Bool(not self.is_true()).set_context(self.context), None

    def anded(self, other):
        return Bool((self.is_true()) and (other.is_true())).set_context(self.context), None

    def ored(self, other):
        return Bool((self.is_true()) or (other.is_true())).set_context(self.context), None

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f"{self.value}"

class Bool(Number):
    def __init__(self, state):
        super().__init__(state)

    def is_type(self, other):
        return Bool(int(other.value == "Bool")), None

    def copy(self):
        copy = Bool(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return "true" if self.value else "false"

class NullType(Number):
    def __init__(self, state):
        super().__init__(0)

    def is_type(self, other):
        return Bool(int(other.value == "NullType")), None

    def copy(self):
        copy = NullType(0)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return "null"


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = str(value)
        self.predefined = {
            "type": "String",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return String(self.value[:int(other.value)]).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(self.context), None
        else:
            return None, self.IllegalOperationError(other)

    def dived_by(self, other):
        if isinstance(other, Number):
            if len(self.value) > other.value:
                return String(self.value[int(other.value)]), None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def ee(self, other):
        if isinstance(other, String):
            return Bool(self.value == other.value).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, String):
            return Bool(self.value != other.value).set_context(self.context), None
        else:
            return Bool(1), None

    def is_true(self):
        return len(self.value) > 0

    def is_type(self, other):
        return Bool(int(other.value == "String")), None

    def notted(self):
        return Bool(not self.is_true()).set_context(self.context), None

    def anded(self, other):
        return Bool((self.is_true()) and (other.is_true())).set_context(self.context), None

    def ored(self, other):
        return Bool((self.is_true()) or (other.is_true())).set_context(self.context), None

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f"{self.value}"


class BaseFunction(Value):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.predefined = {
            "type": "Function",
            "id": id(self),
            "value": self
        }

    def is_type(self, other):
        return Bool(int(other.value == "Function")), None

    def generate_new_context(self):
        new_context = Context(self.name, self.scope, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self, arg_names, args):
        res = RTResult()
        if len(args)>len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                self.context,
                f"{len(args) - len(arg_names)} too many args passed into '{self.name}'"
            ))
        elif len(args)<len(arg_names):
            return res.failure(RTError(
                self.pos_start, self.pos_end,
                self.context,
                f"{len(args) - len(arg_names)} too few args passed into '{self.name}'"
            ))
        return res.success(null)

    def populate_args(self, arg_names, args, exec_ctx):
        for i in range(len(args)):
            arg_name = arg_names[i]
            arg_value = args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name, arg_value)

    def check_and_populate_args(self, arg_names, args, exec_ctx):
        res = RTResult()
        res.register(self.check_args(arg_names, args))
        if res.should_return(): return res
        self.populate_args(arg_names, args, exec_ctx)
        return res.success(null)

class Function(BaseFunction):
    def __init__(self, name, body, arg_names, scope):
        super().__init__(name)
        self.name = name or "anonymous"
        self.body = body
        self.arg_names = arg_names
        self.scope = scope

    def execute(self, args):
        res = RTResult()
        interpreter = Interpreter()
        exec_ctx = self.generate_new_context()
        res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
        if res.should_return(): return res
        value = res.register(interpreter.visit(self.body, exec_ctx))
        if res.should_return(): return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body, self.arg_names, self.scope)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f"{self.name}({self.arg_names})" + " " + "{" + f"{self.body}" + "}"

class FunContainer(BaseFunction):
    def __init__(self, name, functions, default):
        super().__init__(name)
        self.name = name
        self.functions = functions
        self.default = default

    def execute(self, args):
        res = RTResult()
        for function in self.functions:
            if len(function.arg_names) == len(args):
                to_return = res.register(function.execute(args))
                if res.should_return(): return res
                if isinstance(to_return, NullType):
                    continue
                return res.success(to_return)
        if self.default:
            if len(self.default.arg_names) == len(args):
                to_return = res.register(self.default.execute(args))
                if res.should_return(): return res
                return res.success(to_return)
            return res.failure(RTError(
                self.default.pos_start, self.default.pos_end,
                self.default.context,
                f"No Pattern including default pattern {self.default.name} matched"
            ))
        return res.success(null)

    def copy(self):
        new_container = FunContainer(self.name, [x.copy() for x in self.functions], self.default)
        return new_container

    def __repr__(self):
        return f"{self.name} " + "{" + f"{self.functions}" + "}" + f" else {self.default}"


class List(Value):
    def __init__(self, value, isarg=False):
        super().__init__()
        self.value = value
        self.isarg = isarg
        self.predefined = {
            "type": "List",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        new_list = List(self.value[:]).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        new_list.value.append(other)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            if len(self.value) > other.value:
                new_list = List(self.value[:]).set_pos(self.pos_start, self.pos_end).set_context(self.context)
                new_list.value.pop(int(other.value))
                return new_list, None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return None, Value.IllegalOperationError(self, other)
        else:
            new_list = List(self.value[:]).set_pos(self.pos_start, self.pos_end).set_context(self.context)
            new_list.value.extend(other.value)
            return new_list, None

    def dived_by(self, other):
        if isinstance(other, Number):
            if len(self.value) > other.value:
                return self.value[int(other.value)], None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def truth_of_list(self, other):
        truth = []
        if len(other.value) != len(self.value): return False
        if not isinstance(other, List): return False
        for index, element in enumerate(self.value):
            if (0 <= index) and (index < len(other.value)):
                call = self.value[index].ee(other.value[index])[0]
                if call:
                    if call.value == 1:
                        truth.append(True)
                    else:
                        break
                else:
                    break
        return (len(truth) == len(self.value)) and (len(truth) == len(other.value))

    def ee(self, other):
        if isinstance(other, List):
            return Bool(int(self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, List):
            return Bool(int(not self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(1), None

    def is_true(self):
        return len(self.value)>0

    def is_type(self, other):
        return Bool(int(other.value == "List")), None

    def notted(self):
        return Bool(not self.is_true()), None

    def ored_by(self, other):
        if isinstance(other, List):
            result = self.is_true() or other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def argpowed(self):
        new_list = List(self.value[:]).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        new_list.isarg = True
        return new_list, None

    def anded_by(self, other):
        if isinstance(other, List):
            result = self.is_true() and other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def copy(self):
        copy = List(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

class Tuple(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.predefined = {
            "type": "Tuple",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        new_list = Tuple(self.value + (other, )).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number):
            if len(self.value) > other.value:
                list_value = list(self.value)
                list_value.pop(int(other.value))
                new_list = Map(tuple(list_value)).set_pos(self.pos_start, self.pos_end).set_context(self.context)
                return new_list, None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def multed_by(self, other):
        if not isinstance(other, Tuple):
            return None, Value.IllegalOperationError(self, other)
        new_list = Tuple(self.value + other.value).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_list, None

    def dived_by(self, other):
        if isinstance(other, Number):
            if len(self.value) > other.value:
                return self.value[int(other.value)], None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def truth_of_list(self, other):
        truth = []
        if len(other.value) != len(self.value): return False
        if not isinstance(other, List): return False
        for index, element in enumerate(self.value):
            if (0 <= index) and (index < len(other.value)):
                call = self.value[index].ee(other.value[index])[0]
                if call:
                    if call.value == 1:
                        truth.append(True)
                    else:
                        break
                else:
                    break
        return (len(truth) == len(self.value)) and (len(truth) == len(other.value))

    def ee(self, other):
        if isinstance(other, List):
            return Bool(int(self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, List):
            return Bool(int(not self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(1), None

    def is_true(self):
        return len(self.value)>0

    def is_type(self, other):
        return Bool(int(other.value == "Tuple")), None

    def notted(self):
        return Bool(not self.is_true()), None

    def ored_by(self, other):
        if isinstance(other, List):
            result = self.is_true() or other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def argpowed(self):
        new_list = List(self.value[:]).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        new_list.isarg = True
        return new_list, None

    def anded_by(self, other):
        if isinstance(other, List):
            result = self.is_true() and other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def copy(self):
        copy = Tuple(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

class Set(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.representative = [str(value) for key, value in self.value.items()]
        self.predefined = {
            "type": "Set",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        if not ((isinstance(other, Number)) or (isinstance(other, String))):
            return None, Value.IllegalOperationError(self, other)
        new_list = deepcopy(self.value)
        new_list[other.value] = other
        new_list = Set(new_list).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_list, None

    def subbed_by(self, other):
        if isinstance(other, Number) or isinstance(other, String):
            if other.value in self.value:
                new_list = deepcopy(self.value)
                del new_list[other.value]
                new_list = Set(new_list).set_pos(self.pos_start, self.pos_end).set_context(self.context)
                return new_list, None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def multed_by(self, other):
        new_list = {}
        new_list.update(self.value)
        new_list.update(other.value)
        new_list = Set(new_list).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_list, None

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value in self.value:
                return self.value[int(other.value)], None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def truth_of_list(self, other):
        truth = []
        if len(other.value) != len(self.value): return False
        if not isinstance(other, Set): return False
        for index, element in self.value.items():
            if index in other.value:
                call = element.ee(other.value[index])[0]
                if call:
                    if call.value == 1:
                        truth.append(True)
                    else:
                        break
                else:
                    break
        return (len(truth) == len(self.value)) and (len(truth) == len(other.value))

    def ee(self, other):
        if isinstance(other, Set):
            return Bool(int(self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, Set):
            return Bool(int(not self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(1), None

    def is_true(self):
        return len(self.value)>0

    def is_type(self, other):
        return Bool(int(other.value == "Set")), None

    def notted(self):
        return Bool(not self.is_true()), None

    def ored_by(self, other):
        if isinstance(other, List):
            result = self.is_true() or other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def anded_by(self, other):
        if isinstance(other, List):
            result = self.is_true() and other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def copy(self):
        copy = Set(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return "{"+f"{', '.join(self.representative)}"+"}"

class Map(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.value_map = {key.value: value for key, value in self.value.items()}
        self.predefined = {
            "type": "Map",
            "id": id(self),
            "value": self
        }

    def added_to(self, other):
        new_map = {}
        if not (isinstance(other, Set) or isinstance(other, Map)):
            return None, Value.IllegalOperationError(self, other)
        new_map.update(self.value)
        new_map.update(other.value)
        new_map = Map(new_map).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_map, None

    def subbed_by(self, other):
        if (isinstance(other, String)) or (isinstance(other, Number)):
            if other.value in self.value:
                new_map = deepcopy(self.value)
                new_map = Map(new_map).set_pos(self.pos_start, self.pos_end).set_context(self.context)
                del new_map[other.value]
                return new_list, None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def dived_by(self, other):
        if (isinstance(other, String)) or (isinstance(other, Number)):
            if other.value in self.value_map:
                return self.value_map[other.value], None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def get_property(self, other):
        if (isinstance(other, Token)) and other.type == TT_IDENTIFIER:
            val = self.value_map.get(other.value)
            if val is None:
                return null.set_context(self.context).set_pos(self.pos_start, other.pos_end), None
            return val, None
        else:
            return self.dived_by(other)

    def truth_of_list(self, other):
        truth = []
        if len(other.value) != len(self.value): return False
        if not isinstance(other, Map): return False
        for index, element in self.value.items():
            if index in other.value:
                call = self.value[index].ee(other.value[index])[0]
                if call:
                    if call.value == 1:
                        truth.append(True)
                    else:
                        break
                else:
                    break
        return (len(truth) == len(self.value)) and (len(truth) == len(other.value))

    def ee(self, other):
        if isinstance(other, List):
            return Bool(int(self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(0), None

    def ne(self, other):
        if isinstance(other, List):
            return Bool(int(not self.truth_of_list(other))).set_context(self.context), None
        else:
            return Bool(1), None

    def is_type(self, other):
        return Bool(int(other.value == "Map")), None

    def is_true(self):
        return len(self.value)>0

    def notted(self):
        return Bool(not self.is_true()), None

    def ored_by(self, other):
        if isinstance(other, List):
            result = self.is_true() or other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def anded_by(self, other):
        if isinstance(other, List):
            result = self.is_true() and other.is_true()
            return Bool(result).set_context(self.context), None
        else:
            return None, Value.IllegalOperationError(self, other)

    def copy(self):
        copy = Map(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return str(self.value)

class Record(Map):
    def __init__(self, types, elements):
        super().__init__(elements)
        self.value = elements
        self.predefined = {
            "types": types[:],
            "id": id(elements)
        }

    def added_to(self, other):
        new_map = {}
        if not (isinstance(other, Set) or isinstance(other, Map)):
            return None, Value.IllegalOperationError(self, other)
        new_map.update(self.value)
        new_map.update(other.value)
        new_map = Record(self.predefined['types'], new_map).set_pos(self.pos_start, self.pos_end).set_context(self.context)
        return new_map, None

    def subbed_by(self, other):
        if (isinstance(other, String)) or (isinstance(other, Number)):
            if other.value in self.value:
                new_map = deepcopy(self.value)
                new_map = Record(self.predefined['types'], new_map).set_pos(self.pos_start, self.pos_end).set_context(self.context)
                del new_map[other.value]
                return new_list, None
            else:
                return None, RTError(
                    other.pos_start, other.pos_end,
                    self.context,
                    "Index out of bounds"
                )
        else:
            return None, Value.IllegalOperationError(self, other)

    def get_property(self, other):
        if (isinstance(other, Token)) and other.type == TT_IDENTIFIER:
            val = self.value_map.get(other.value)
            if val is None:
                if other.value in self.predefined:
                    return self.predefined[other.value], None
                elif other.value == "type":
                    return String(self.predefined['types'][-1]), None
                return null.set_context(self.context).set_pos(self.pos_start, other.pos_end), None
            return val, None
        else:
            return self.dived_by(other)

    def is_type(self, other):
        return Bool(int(other.predefined["types"][-1] in self.predefined["types"]) if isinstance(other, Record) else int(other.value in self.predefined["types"])), None

    def copy(self):
        copy = Record(self.predefined['types'], self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f"{self.predefined['types'][-1]} {str(self.value)}" if self.value else f"{self.predefined['types'][-1]}"

class Extensor(Value):
    def __init__(self):
        super().__init__()

    def added_to(self, other):
        return self.copy(), None

    def subbed_by(self, other):
        return self.copy(), None

    def multed_by(self, other):
        return self.copy(), None

    def dived_by(self, other):
        return self.copy(), None

    def lt(self, other):
        return self.copy(), None

    def lte(self, other):
        return self.copy(), None

    def gt(self, other):
        return self.copy(), None

    def gte(self, other):
        return self.copy(), None

    def ee(self, other):
        return self.copy(), None

    def ne(self, other):
        return self.copy(), None

    def execute(self, args):
        return self.copy(), None

    def argpowed(self):
        return self.copy(), None

    def is_type(self, other):
        return Bool(1), None

    def get_property(self, other):
        return self.copy(), None

    def is_true(self):
        return Bool(1)

    def copy(self):
        copy = Extensor()
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos=None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos
        self.symbol_table = None

    def copy(self):
        new_context = Context(self.display_name, self.parent, self.parent_entry_pos)
        new_context.symbol_table = self.symbol_table.copy()
        return new_context

    def __repr__(self):
        return f"<{self.display_name}>"

class SymbolTable:
    def __init__(self, parent=None):
        self.symbol_table = {}
        self.parent = parent

    def get(self, name):
        out = self.symbol_table.get(name, None)
        if (out is None) and (self.parent):
            out = self.parent.get(name)
        return out

    def set(self, name, value):
        self.symbol_table[name] = value
        return value

    def copy(self):
        new_table = SymbolTable(self.parent)
        new_table.symbol_table = self.symbol_table
        return new_table

    def __repr__(self):
        return f"{str(self.symbol_table)} -> {str(self.parent)}"


class Interpreter:
    def visit(self, node, context):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self, node, context):
        raise Exception(f"visit_{type(node).__name__} is undefined")

    def visit_NumberNode(self, node, context):
        return RTResult().success(
            Number(node.number).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_StringNode(self, node, context):
        return RTResult().success(
            String(node.string).set_pos(node.pos_start, node.pos_end).set_context(context)
        )

    def visit_ListNode(self, node, context):
        res = RTResult()
        elements = []
        for element in node.elements:
            element_value = res.register(self.visit(element, context))
            if isinstance(element_value, List) and element_value.isarg:
                elements.extend(element_value.value)
            else:
                elements.append(element_value)
            if res.should_return(): return res
        return res.success(
                List(elements, node.isArg).set_context(context).set_pos(node.pos_start, node.pos_end)
            )

    def visit_TupleNode(self, node, context):
        res = RTResult()
        elements = []
        for element in node.elements:
            elements.append(res.register(self.visit(element, context)))
            if res.should_return(): return res
        return res.success(
                Tuple(tuple(elements)).set_context(context).set_pos(node.pos_start, node.pos_end)
            )

    def visit_SetNode(self, node, context):
        res = RTResult()
        elements = []
        for element in node.elements:
            element_value = res.register(self.visit(element, context))
            if res.should_return(): return res
            if isinstance(element_value, List) and element_value.isarg:
                for elem in element_value.value:
                    if not ((isinstance(elem, String)) or (isinstance(elem, Number))):
                        return res.failure(RTError(
                            node.pos_start, node.pos_end,
                            context,
                            f"Unhashable element {elem}"
                        ))
                    elements.append(elem)
            else:
                if not ((isinstance(element_value, String)) or (isinstance(element_value, Number))):
                    return res.failure(RTError(
                        node.pos_start, node.pos_end,
                        context,
                        f"Unhashable element {element_value}"
                    ))
                elements.append(element_value)
        elements = {k.value: k for k in elements}
        return res.success(
                Set(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )

    def visit_MapNode(self, node, context):
        res = RTResult()
        elements = {}
        for key, value in node.elements:
            key_value = res.register(self.visit(key, context))
            if res.should_return(): return res
            elements[key_value] = res.register(self.visit(value, context))
            if res.should_return(): return res
        return res.success(
                Map(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )

    def visit_RecordInstanceNode(self, node, context):
        res = RTResult()
        elements = {}
        type_ = res.register(self.visit(node.type, context))
        types = node.types[:]
        if res.error: return res
        for key, value in node.elements:
            key_value = res.register(self.visit(key, context))
            if res.should_return(): return res
            elements[key_value] = res.register(self.visit(value, context))
            if res.should_return(): return res
        return res.success(
                Record(types, elements).set_context(context).set_pos(node.pos_start, node.pos_end)
            )

    def visit_UnaryNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.number, context))
        if res.should_return(): return res
        error = None
        if node.unary.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.unary.matches(TT_KEYWORD, "not"):
            number, error = number.notted()
        elif node.unary.type == TT_ARGPOW:
            number, error = number.argpowed()
        elif node.unary.type == TT_DCOLON:
            number, error = number.get_property(Token(TT_IDENTIFIER, "type"))
        if error: return res.failure(error)
        return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_FuncDefNode(self, node, context):
        res = RTResult()
        func_name = node.identifier.value if node.identifier else node.identifier
        func_args = [arg.value for arg in node.args]
        func_body = node.expr
        func_value = Function(func_name, func_body, func_args, context.copy()).set_context(context).set_pos(node.pos_start, node.pos_end)
        if node.identifier:
            res.register(immutableCheck(func_name, context, node.pos_start, node.pos_end))
            if res.error: return res
            context.symbol_table.set(func_name, func_value)
        return res.success(func_value)

    def visit_ValNode(self, node, context):
        res = RTResult()
        if len(node.identifiers) > len(node.exprs):
            expr = res.register(self.visit(node.exprs[0], context))
            if res.error: return res
            if isinstance(expr, Tuple):
                 if len(node.identifiers) != len(expr.value):
                    return res.failure(RTError(
                        node.pos_start, node.pos_end,
                        context,
                        f"Unequal expressions and identifiers"
                    ))
                 else:
                    vars = list(zip(node.identifiers, expr.value))
                    for identifier, expr in vars:
                        res.register(immutableCheck(identifier, context, node.pos_start, node.pos_end))
                        if res.error: return res
                        context.symbol_table.set(identifier.value, expr)
                    return res.success(null.set_context(context).set_pos(node.pos_start, node.pos_end))
            else:
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"Unequal expressions and identifiers"
                ))
        elif len(node.identifiers) == len(node.exprs):
            vars = list(zip(node.identifiers, node.exprs))
            for identifier, expr in vars:
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                res.register(immutableCheck(identifier.value, context, node.pos_start, node.pos_end))
                if res.error: return res
                context.symbol_table.set(identifier.value, expr_value)
            return res.success(null.set_context(context).set_pos(node.pos_start, node.pos_end))
        return res.failure(RTError(
            node.pos_start, node.pos_end,
            context,
            f"Unequal expressions and identifiers"
        ))


    def visit_RecordNode(self, node, context):
        res = RTResult()
        func_name = node.type.value
        types = []
        elements = []
        func_args = [arg.value for arg in node.elements]
        if node.extension:
            extension = res.register(self.visit(node.extension, context))
            if res.error: return res
            if not isinstance(extension, Function):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{extension} is not a record"
                ))
            extension_record = res.register(extension.execute([extensor for _ in range(len(extension.arg_names))]))
            if res.error:
                res.reset()
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{extension} is not a record"
                ))
            if not isinstance(extension_record, Record):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{extension} is not a record"
                ))
            extension_keys = [k for k, _ in extension_record.value.items()]
            args = [x.value for x in extension_keys]
            func_args = [*args, *func_args]
            types.extend(extension_record.predefined["types"])
            for key in extension_keys:
                element_name = StringNode(key.value, node.pos_start, node.pos_end)
                element_value = FuncShowNode(Token(TT_IDENTIFIER, key.value), node.pos_start, node.pos_end)
                elements.append((element_name, element_value))
        for element in node.elements:
            element_name = StringNode(element.value, node.pos_start, node.pos_end)
            element_value = FuncShowNode(element, node.pos_start, node.pos_end)
            elements.append((element_name, element_value))
        type_node = StringNode(node.type.value, node.pos_start, node.pos_end)
        type_value = res.register(self.visit(type_node, context))
        types.append(type_value.value)
        if res.error: return res
        func_body = RecordInstanceNode(type_node, types, elements, node.pos_start, node.pos_end)
        if node.when:
            func_body = WhenNode(node.when, func_body, node.pos_start, node.pos_end)
        func_value = Function(func_name, func_body, func_args, context.copy()).set_context(context).set_pos(node.pos_start, node.pos_end)
        res.register(immutableCheck(func_name, context, node.pos_start, node.pos_end))
        if res.error: return res
        context.symbol_table.set(func_name, type_value)
        return res.success(func_value)

    def visit_FunCallNode(self, node, context):
        res = RTResult()
        args = []
        if (isinstance(node.identifier, Token)) and (node.identifier.type == TT_IDENTIFIER):
            value_to_call = context.symbol_table.get(node.identifier.value)
        else:
            value_to_call = res.register(self.visit(node.identifier, context))
            if res.error: return res
        if value_to_call is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.value} is undefined"
            ))
        if not isinstance(value_to_call, BaseFunction):
            return res.success(value_to_call)
        if isinstance(value_to_call, FunCallNode):
            value_to_call = res.register(self.visit(node.identifier, context))
        for arg_node in node.args:
            arg = res.register(self.visit(arg_node, context))
            if res.should_return(): return res
            if (isinstance(arg, List)) and (arg.isarg):
                args.extend(arg.value)
            else:
                args.append(arg)
        return_value = res.register(value_to_call.execute(args))
        if res.should_return(): return res
        return_value = return_value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(return_value)

    def visit_FuncShowNode(self, node, context):
        res = RTResult()
        if (isinstance(node.identifier, Token)) and (node.identifier.type == TT_IDENTIFIER):
            value_to_call = context.symbol_table.get(node.identifier.value)
        else:
            value_to_call = res.register(self.visit(node.identifier, context))
            if res.error: return res
        if value_to_call is None:
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.value} is undefined"
            ))
        return res.success(value_to_call)

    def visit_IfNode(self, node, context):
        res = RTResult()
        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.should_return(): return res
            if condition_value.is_true():
                expr_value = res.register(self.visit(expr, context))
                if res.should_return(): return res
                return res.success(expr_value)
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.should_return(): return res
            return res.success(else_value)
        return res.success(null)

    def visit_WhenNode(self, node, context):
        res = RTResult()
        new_interpreter = Interpreter()
        new_context = Context(id(new_interpreter), context, node.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        statement = res.register(new_interpreter.visit(node.statement, new_context))
        if res.should_return(): return res
        expr = res.register(new_interpreter.visit(node.expr, new_context))
        if res.should_return(): return res
        return res.success(expr)

    def visit_AlgebraDefNode(self, node, context):
        res = RTResult()
        functions = []
        default = None
        node.identifier.type.value = fWordList(node.identifier.type.value, "upper")
        identifier = res.register(self.visit(node.identifier, context))
        if res.error: return res
        if not isinstance(identifier, BaseFunction):
            non_record = fWordList(node.identifier.type.value, "lower")
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{non_record} is not a function"
            ))
        identifier.name = fWordList(identifier.name, "upper")
        new_context = Context(str(id(node)) + identifier.name, context, node.pos_end)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        new_context.symbol_table.set(identifier.name, identifier)
        for conditionNode, recordNode in node.cases:
            recordFunction = res.register(self.visit(recordNode, new_context))
            if res.error: return res
            if not isinstance(recordFunction, BaseFunction):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{recordFunction} is not a function"
                ))
            recordFunctionCopy = recordFunction.copy()
            if (isinstance(recordFunctionCopy.body, RecordInstanceNode) or (isinstance(recordFunctionCopy.body, WhenNode)
                and isinstance(recordFunctionCopy.body.expr, RecordInstanceNode
            ))):
                if isinstance(recordFunctionCopy.body, WhenNode):
                    recordFunction.body.expr.types = [identifier.name, *recordFunction.body.expr.types]
                else:
                    recordFunction.body.types = [identifier.name, *recordFunction.body.types]
            recordFunctionCopy.body = IfNode([(conditionNode, recordFunction.body)], None, recordFunction.pos_start, recordFunction.pos_end)
            if fWordList(recordFunction.name, "lower") in context.symbol_table.symbol_table:
                context.symbol_table.set(fWordList(recordFunction.name, "lower"), recordFunction)
            else:
                context.symbol_table.set(fWordList(recordFunction.name, "lower"), recordFunctionCopy)
            functions.append(recordFunctionCopy)
        if node.default:
            defaultRecordFunction = res.register(self.visit(node.default, new_context))
            if res.error: return res
            if not isinstance(defaultRecordFunction, BaseFunction):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{defaultRecordFunction} is not a function"
                ))
            defaultRecordFunctionCopy = defaultRecordFunction.copy()
            if (isinstance(defaultRecordFunctionCopy.body, RecordInstanceNode) or (isinstance(defaultRecordFunctionCopy.body, WhenNode)
                and isinstance(defaultRecordFunctionCopy.body.expr, RecordInstanceNode
            ))):
                if isinstance(defaultRecordFunctionCopy.body, WhenNode):
                    defaultRecordFunction.body.expr.types = [identifier.name, *recordFunction.body.expr.types]
                else:
                    defaultRecordFunction.body.types = [identifier.name, *recordFunction.body.types]
            if fWordList(defaultRecordFunction.name, "lower") in context.symbol_table.symbol_table:
                context.symbol_table.set(fWordList(defaultRecordFunction.name, "lower"), defaultRecordFunction)
            else:
                context.symbol_table.set(fWordList(defaultRecordFunction.name, "lower"), defaultRecordFunctionCopy)
            default = defaultRecordFunctionCopy
        for c_identifier, c_value in new_context.symbol_table.symbol_table.items():
            if c_identifier[0].isupper():
                res.register(immutableCheck(c_identifier, context, node.pos_start, node.pos_end))
                if res.error:
                    if c_identifier != fWordList(identifier.name, "upper"):
                        return res
                    else:
                        res.reset()
                context.symbol_table.set(c_identifier, c_value)
        res.register(immutableCheck(identifier, context, node.pos_start, node.pos_end))
        if res.error: return res
        context.symbol_table.set(identifier.name, String(identifier.name).set_context(context).set_pos(node.pos_start, node.pos_end))
        fun_name = fWordList(identifier.name, "lower")
        container = FunContainer(fun_name, functions, default).set_context(context).set_pos(node.pos_start, node.pos_end)
        res.register(immutableCheck(fun_name, context, node.pos_start, node.pos_end))
        if res.error: return res
        context.symbol_table.set(fun_name, container)
        return res.success(container)

    def visit_ForNode(self, node, context):
        res = RTResult()
        elements = []
        identifier_expr = res.register(self.visit(node.identifier_expr, context))
        condition = Bool(1)
        if res.error: return res
        if not (isinstance(identifier_expr, List) or isinstance(identifier_expr, Tuple) or isinstance(identifier_expr, String)):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{identifier_expr} is not a List"
            ))
        last_context = context
        for element in identifier_expr.value:
            new_interpreter = Interpreter()
            new_context = Context(id(new_interpreter), last_context, node.pos_start)
            new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
            new_context.symbol_table.set(node.iterator.value, element)
            if node.filter:
                condition = res.register(self.visit(node.filter, new_context))
                if res.should_return(): return res
            if condition.is_true():
                elements.append(res.register(new_interpreter.visit(node.expr, new_context)))
                if res.should_return(): return res
            last_context = new_context
        new_list = List(elements).set_pos(node.pos_start, node.pos_end).set_context(context)
        new_list.isarg = True
        return res.success(new_list)

    def visit_PatternNode(self, node, context):
        res = RTResult()
        new_interpreter = Interpreter()
        new_context = Context(id(new_interpreter), context, node.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
        if node.map_context is not None:
            map_context = res.register(self.visit(node.map_context, context))
            if res.should_return(): return res
            if not isinstance(map_context, Map):
                return res.failure(RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{map_context} is neither a map nor a Record Instance"
                ))
            new_context.symbol_table.symbol_table = map_context.copy().value_map
        for identifier, expr in node.vars:
            expr_value = res.register(new_interpreter.visit(expr, new_context))
            res.register(immutableCheck(func_name, context, node.pos_start, node.pos_end))
            if res.error: return res
            new_context.symbol_table.set(identifier.value, expr_value)
        endres = res.register(new_interpreter.visit(node.node, new_context))
        if res.error: return res
        return res.success(endres)

    def visit_AddCaseNode(self, node, context):
        res = RTResult()
        function = res.register(self.visit(node.identifier, context))
        if res.error: return res
        if not isinstance(function, Function):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.identifier.value} is not a caseable function"
            ))
        if not isinstance(function.body, PatternNode):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.identifier.value} is not a caseable function"
            ))
        if not isinstance(function.body.node, IfNode):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.identifier.value} is not a caseable function"
            ))
        if node.condition:
            function.body.node.cases.append((node.condition, node.expr))
        else:
            function.body.node.else_case = node.expr
        return res.success(null)

    def visit_AddAlgebraCaseNode(self, node, context):
        res = RTResult()
        funcontainer = res.register(self.visit(node.identifier, context))
        if res.error: return res
        function = res.register(self.visit(node.expr, context))
        if res.error: return res
        if not isinstance(funcontainer, FunContainer):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{node.identifier.identifier.value} is not a caseable function"
            ))
        if not isinstance(function, BaseFunction):
            return res.failure(RTError(
                node.pos_start, node.pos_end,
                context,
                f"{function} is not a function"
            ))
        upperFunContainerName = fWordList(funcontainer.name, "upper")
        upperFunctionName = fWordList(function.name, "upper")
        lowerFunctionName = fWordList(function.name, "lower")
        if (isinstance(function.body, RecordInstanceNode) or (isinstance(function.body, WhenNode)
        and isinstance(function.body.expr, RecordInstanceNode))):
            if isinstance(function.body, WhenNode):
                function.body.expr.types = [upperFunContainerName, *function.body.expr.types]
            else:
                function.body.types = [upperFunContainerName, *function.body.types]
        functionCopy = function.copy()
        functionCopy.body = IfNode([(node.condition, function.body)], None, node.pos_start, node.pos_end)
        funcontainer.functions.append(functionCopy)
        context.symbol_table.set(upperFunctionName, String(upperFunctionName).set_context(context).set_pos(node.pos_start, node.pos_end))
        if lowerFunctionName in context.symbol_table.symbol_table:
            context.symbol_table.set(lowerFunctionName, function)
        else:
            context.symbol_table.set(lowerFunctionName, functionCopy)
        return res.success(null)

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left, context))
        if res.should_return(): return res
        if node.op.type == TT_DARROW and isinstance(node.right, FunCallNode):
            right = node.right
        else:
            right = res.register(self.visit(node.right, context))
        if res.should_return(): return res
        error = None
        result = None
        if node.op.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op.type == TT_GT:
            result, error = left.gt(right)
        elif node.op.type == TT_GTE:
            result, error = left.gte(right)
        elif node.op.type == TT_LT:
            result, error = left.lt(right)
        elif node.op.type == TT_LTE:
            result, error = left.lte(right)
        elif node.op.type == TT_EE:
            result, error = left.ee(right)
        elif node.op.type == TT_NE:
            result, error = left.ne(right)
        elif node.op.type == TT_INFIX:
            id = node.op.value
            fun = context.symbol_table.get(id)
            if isinstance(fun, BaseFunction):
                result = res.register(fun.execute([left, right]))
                if res.error: error = res.error
            else:
                error = RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{id} is not a function"
                )
        elif node.op.type == TT_PIPELINE:
            fun = right
            if isinstance(fun, BaseFunction):
                result = res.register(fun.execute(left.value if (isinstance(left, List) and left.isarg) else [left]))
                if res.error: error = res.error
            else:
                error = RTError(
                    node.pos_start, node.pos_end,
                    context,
                    f"{id} is not a function"
                )
        elif node.op.type == TT_DCOLON:
            result, error = left.is_type(right)
        elif node.op.type == TT_DARROW:
            if isinstance(right, FunCallNode):
                right = right.identifier
            result, error = left.get_property(right)
        elif node.op.matches(TT_KEYWORD, "and"):
            result, error = left.anded(right)
        elif node.op.matches(TT_KEYWORD, "or"):
            result, error = left.ored(right)
        if error: return res.failure(error)
        return res.success(result.set_pos(node.pos_start, node.pos_end))

false = Bool(0)
true = Bool(1)
null = NullType(0)
extensor = Extensor()
global_symbol_table = SymbolTable()
global_symbol_table.set('false', false)
global_symbol_table.set('true', true)
global_symbol_table.set('null', null)
global_symbol_table.set('String', String("String"))
global_symbol_table.set('Number', String("Number"))
global_symbol_table.set('List', String("List"))
global_symbol_table.set('Tuple', String("Tuple"))
global_symbol_table.set('Map', String("Map"))
global_symbol_table.set('Set', String("Set"))
global_symbol_table.set('Function', String("Function"))
global_symbol_table.set('Bool', String("Bool"))
global_symbol_table.set('NullType', String("NullType"))

def immutableCheck(name, context, pos_start, pos_end):
    res = RTResult()
    if name in context.symbol_table.symbol_table:
        return res.failure(RTError(
            pos_start, pos_end,
            context,
            f"Cannot change immutable variable {name}"
        ))
    else:
        return res.success(null)

def fWordList(name, todo):
    fun_name = list(name)
    fun_name[0] = fun_name[0].upper() if todo == "upper" else fun_name[0].lower()
    fun_name = "".join(fun_name)
    return fun_name

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.generate_tokens()
    if error: return None, error
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error
    interpreter = Interpreter()
    context = Context(fn)
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)
    return result.value, result.error

while True:
    inp = input("Dyha>> ")
    res, error = run("<module>", inp)
    if error:
        print(error.as_string())
    else:
        if len(res.value) > 1:
            print(res)
        else:
            print(res.value[0])
