import imp

from functools import partial

__version__ = '0.0.1b0'


def get_pyparsing(name):
    if name is None:
        import pyparsing as module
        return module
    if getattr(name, 'ParserElement', None):
        return name
    mpath = imp.find_module('pyparsing')
    return imp.load_module(name, *mpath)


class FutureToken(object):
    pass


class ParseAction(object):
    def __init__(self, name, parser, fnc):
        self.parser = parser
        self.name = name
        self.fnc = fnc

    @property
    def expr(self):
        return self.parser._compile(self.name)

    def parseString(self, string, parseAll=True):
        return self.expr.parseString(string, parseAll=parseAll)


class Parser(object):
    def __init__(self, pubparser=None, auto_cache=True):
        self.pubparser = get_pyparsing(pubparser)
        self.privparser = get_pyparsing('privparser%s' % id(self))
        self.auto_cache = True
        self.cache = {}

        self.expr = {
            k: v
            for k, v in self.pubparser.pyparsing_common.__dict__.items()
            if isinstance(v, self.pubparser.ParserElement)
        }

        self.methods = {
            'delimitedList': self.pubparser.delimitedList,
        }

        self.tokens = {}

    def _compile(self, token, **kargs):
        preparser = self.privparser
        preparser.ParserElement.setDefaultWhitespaceChars('')

        cache_key = kargs.get('cache', self.auto_cache)
        if cache_key and cache_key not in self.cache:
            self.cache[cache_key] = {}

        TOKENS = self.cache[cache_key] if cache_key else {}
        PEGPARSER = preparser.Forward()

        def get_token(token):
            # lets se if we already parsd the token
            tok = TOKENS.get(token)

            if isinstance(tok, FutureToken):
                # this token is in the parsing tree, so its a recursive token.
                TOKENS[token] = self.pubparser.Forward()
                return TOKENS[token]

            if tok is not None:
                # normal token, give it away
                return tok

            # we dont know the token, time to parse it from expr
            expr = self.expr[token]

            if isinstance(expr, (list, tuple,)):
                k, v = expr
            else:
                k, v = expr, None

            if isinstance(k, self.pubparser.ParserElement):
                if v:
                    TOKENS[token] = k.setParseAction(v)
                else:
                    TOKENS[token] = k

                return TOKENS[token]

            TOKENS[token] = FutureToken()

            parsed_expr = PEGPARSER.parseString(k.strip(), parseAll=True)

            p = parsed_expr[0]

            if v:
                p = p.setParseAction(v)

            if isinstance(TOKENS[token], FutureToken):
                TOKENS[token] = p
            else:
                TOKENS[token] << p

            return TOKENS[token]

        WS = (
            preparser.Literal(" ") |
            preparser.Literal("\t") |
            preparser.Literal("\n")
        )

        def apply_method(method, varargs):
            for arg in varargs:
                if isinstance(arg, dict):
                    method = partial(method, **arg)
                else:
                    method = partial(method, arg)
            result = method()
            return result

        def optional_ws(x):
            return (
                preparser.ZeroOrMore(WS).suppress() +
                x +
                preparser.ZeroOrMore(WS).suppress()
            )

        qstring = (
            preparser.QuotedString("'") | preparser.QuotedString('"')
        ).setParseAction(
            lambda t: self.pubparser.Literal(t[0]))

        regex = preparser.QuotedString('/').setParseAction(
            lambda t: self.pubparser.Regex(t[0]))

        token_ident = preparser.pyparsing_common\
            .identifier.copy().setParseAction(
                lambda t: get_token(t[0])
            )

        name_dentifier = (
            preparser.Literal("@") +
            preparser.pyparsing_common.identifier.copy()
        ).setParseAction(
            lambda r: {'name': r[1]}
        )

        method = preparser.Forward()

        operand = name_dentifier | token_ident | qstring | regex | method

        method_name = (
            preparser.Literal('$') +
            preparser.pyparsing_common.identifier
        ).setParseAction(
            lambda r: self.methods[r[1]]
        )

        method_argument = preparser.Optional(name_dentifier + preparser.Suppress(":")) + (
            optional_ws(token_ident) |
            optional_ws(qstring) |
            optional_ws(regex) |
            optional_ws(method) |
            optional_ws(method_name)
        )

        method_argument = method_argument.setParseAction(
            lambda x: x[0] if len(x) == 1 else {x[0]['name']: x[1]})

        method_arguments = preparser.delimitedList(method_argument)

        method << (
            method_name +
            preparser.Literal('[').suppress() +
            method_arguments +
            preparser.Literal(']').suppress()
        ).setParseAction(
            lambda x: apply_method(x[0], x[1:])
        )

        _optional = preparser.Literal('?').setParseAction(
            lambda u: self.pubparser.Optional)
        _zero_or_more = preparser.Literal('*').setParseAction(
            lambda u: self.pubparser.ZeroOrMore)
        _one_or_more = preparser.Literal('+').setParseAction(
            lambda u: self.pubparser.OneOrMore)
        _ignore = preparser.Literal('!').setParseAction(
            lambda u: self.pubparser.Suppress)

        def nameAction(x, y):
            return y.setResultsName(x['name'])

        _names = preparser.Literal(':').setParseAction(
            lambda u: nameAction)
        _and = (preparser.OneOrMore(WS)).setParseAction(
            lambda u: lambda x, y: x + y)

        _or = (
            preparser.ZeroOrMore(WS) +
            preparser.Literal("|") +
            preparser.ZeroOrMore(WS)
        ).setParseAction(
            lambda u: lambda x, y: x | y)

        def infix(x):
            l = list(x[0])
            while len(l) > 1:
                a, o, b = l.pop(0), l.pop(0), l.pop(0)
                l.insert(0, o(a, b))
            if l:
                return l[0]

        def postfix(x):
            l = list(x[0])
            return l[1](l[0])

        PEGPARSER << preparser.operatorPrecedence(
            operand,
            [
                (_optional, 1, preparser.opAssoc.LEFT, postfix),
                (_zero_or_more, 1, preparser.opAssoc.LEFT, postfix),
                (_one_or_more, 1, preparser.opAssoc.LEFT, postfix),

                (_names, 2, preparser.opAssoc.LEFT, infix),
                (_ignore, 1, preparser.opAssoc.LEFT, postfix),

                (_or | _and, 2, preparser.opAssoc.LEFT, infix),

            ]
        )

        return get_token(token)

    def compile(self):
        self.tokens = {
            k: v
            if isinstance(v, self.pubparser.ParserElement)
            else self.pubparser.Forward()
            for k, v in self.expr.items()
        }

        for k, v in self.expr.items():
            if isinstance(v, self.pubparser.ParserElement):
                continue

            if isinstance(v, (tuple, list,)):
                v0, v1 = v
            else:
                v0, v1 = (v, lambda x: x)

            self.tokens[k] = self.peg(v0, name=k)(v1)
        return self.tokens

    def peg(self, peg_expr, name=None):
        parser = self

        def binder(fnc):
            _name = name if name else fnc.__name__

            parser.expr.update({
                _name: (peg_expr, fnc)
            })

            return ParseAction(_name, parser, fnc)

        return binder

    def method(self, fnc):
        self.methods.update({
            fnc.__name__: fnc
        })
        return fnc
