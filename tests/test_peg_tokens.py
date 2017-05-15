


def test_regex_token(parser, pyparsing):
    parser.expr['regx'] = r'/\d/'
    c = parser.compile()
    assert isinstance(c['regx'].expr, pyparsing.Regex)
    assert c['regx'].expr.pattern == r'\d'

def test_quoted_string_token(parser, pyparsing):
    parser.expr.update({
        'st': '"str1"',
        'dt': "'str2'",
    })
    c = parser.compile()
    assert isinstance(c['st'].expr, pyparsing.Literal)
    assert c['st'].expr.match == "str1"
    assert isinstance(c['dt'].expr, pyparsing.Literal)
    assert c['dt'].expr.match == "str2"

def test_token_token(parser, pyparsing):
    parser.expr.update({
        'st': '"test1"',
        'll': "st",
    })
    c = parser.compile()
    assert c['ll'].expr.expr == c['st'].expr
