
# Each token has to have a parse(self, str/byte) where to search
# this should return a ParseResult.
#
# a ParseResult is a class that has 2 main elements, a array containing result

"""
"hello" = R<hello>
"hello world" = ['hello', 'world']
"hello world" = R[R<'hello'>, R<'world'>]


"""

import re

from functools import lru_cache
from contextlib import suppress

@lru_cache()
def regex(*args, **kwargs):
    return re.compile(*args, **kwargs)


class TokenNotFoundError(Exception):
    pass


class BaseToken:
    def __init__(self, ws=None, end_ws=None):
        self.ws = ws or regex('\s*')
        self.end_ws = end_ws or regex('\s*')
    
    @classmethod
    def parse_expr(cls, expr, instr, start):
        match_obj = expr.match(instr, start)
        
        if match_obj:
            return match_obj, match_obj.end()
        
        return None, start

    def parse_ws(self, instr, start):
        if not self.ws:
            return start

        match_obj = self.ws.match(instr, start)

        if match_obj:
            return match_obj.end()

        return start

    def parse_inner(self, instr, start):
        raise NotImplementedError('implement me!')
    
    def _parse(self, instr, start):
        if self.ws:
            _, start = BaseToken.parse_expr(self.ws, instr, start)
        return self.parse_inner(instr, start)
    
    def parse(self, instr, parse_all=True):
        result, end = self._parse(instr, start=0)
        if parse_all:
            if end != len(instr):
                _, end = BaseToken.parse_expr(self.ws or self.end_ws, instr, end)
            if end != len(instr):
                raise Exception("could not parse")
        return result


class ComplexToken(BaseToken):
    def __init__(self, exprs):
        super().__init__()
        self.ws = None

        self.exprs=exprs

class ParseResult:
    def __init__(self, elem=None, names=None):
        self.elem = None if elem is None else elem
        self.names = names or {}
    
    def __repr__(self):
        return f'<{self.elem} {self.names}>'
    

class Token(BaseToken):
    def __init__(self, expr):
        super().__init__()
        self.expr = expr
    
    def parse_inner(self, instr, start):
        match_obj = self.expr.match(instr, start)
        if match_obj:
            return ParseResult(elem=match_obj.group(), names=match_obj.groupdict()), match_obj.end()
        raise TokenNotFoundError()


# matchs

class MatchSequence(ComplexToken):
    def parse_inner(self, instr, start):
        next_start = start
        final_result = ParseResult([], {})
        for expr in self.exprs:
            result, next_start = expr._parse(instr, next_start)
            final_result.elem.append(result)
            final_result.names.update(result.names)
        return final_result, next_start

class MatchFirst(ComplexToken):
    def parse_inner(self, instr, start):
        for expr in self.exprs:
            with suppress(TokenNotFoundError):
                return expr._parse(instr, start)
        raise TokenNotFoundError()

class MatchNtoM(Token):
    def __init__(self, expr, n=0, m=None):
        super().__init__(expr)
        self.n = n
        self.m = m
    
    def parse_inner(self, instr, start):
        next_start = start
        found_count = 0
        final_result = ParseResult([], {})
        
        for _ in range(self.n):
            result, next_start = self.expr._parse(instr, next_start)
            if not result:
                raise TokenNotFoundError()
        
        for _ in range(self.n, self.m):
            result, next_start = self.expr._parse(instr, next_start)
            if not result:
                break

        return final_result, next_start

if __name__ == '__main__':
    b = BaseToken()
    s = b.parse_ws(" \t \t \n\n text starts here     ", 0)
    print(f'string starts at {s}')


    hello = Token(regex('hello'))
    world = Token(regex('world'))
    print(hello.parse('     hello'))
    hello_world = MatchSequence([hello, world])
    hello_or_world = MatchFirst([hello, world])

    print(hello_world.parse("    hello   world"))
    print(hello_or_world.parse("    world"))
    print(hello_or_world.parse("    hello  "))

    easy = MatchSequence([
        MatchFirst([Token(regex('hello')), Token(regex('hi'))]),
        Token(regex('world'))
    ])
    print(easy.parse("    hi world  "))
