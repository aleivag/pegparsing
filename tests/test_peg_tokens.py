
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
    assert c['ll'].expr.name == c['st'].expr.name
    assert c['ll'].parseString('test1')[0] == 'test1'
    assert c['st'].parseString('test1')[0] == 'test1'


def test_same_token(parser):
    parser.expr.update({
        'st': '"test1"',
        'll': "st",
    })
    c1 = parser.compile()
    c2 = parser.compile()

    assert c1['ll'].expr is c1['ll'].expr
    assert c1['ll'].expr is c2['ll'].expr


def test_diferent_token_no_cache(parser):
    parser.auto_cache = False
    parser.expr.update({
        'st': '"test1"',
        'll': "st",
    })
    c1 = parser.compile()
    c2 = parser.compile()

    assert c1['ll'].expr is not c1['ll'].expr
    assert c1['ll'].expr is not c2['ll'].expr
