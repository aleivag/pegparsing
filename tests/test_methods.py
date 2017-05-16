
def test_build_in_method(parser):
    parser.expr.update({
        'test': '$delimitedList[number]',
    })

    compiled = parser.compile()

    assert list(compiled['test'].parseString('1,42,3,4')) == [1, 42, 3, 4]


def test_custom_method(parser):
    def echo(x):
        return x
    parser.methods.update({
        'echo': echo
    })
    parser.expr.update({
        'test': '$echo[number]',
    })

    c = parser.compile()
    assert list(c['test'].parseString('1')) == [1]


def test_multiple_arguments_method(parser, pyparsing):
    def OR(x, y):
        return x | y
    parser.methods.update({
        'or': OR
    })
    parser.expr.update({
        'test': '$or[number,identifier]',
    })

    c = parser.compile()
    assert list(c['test'].parseString('1')) == [1]
    assert list(c['test'].parseString('alvaro')) == ['alvaro']


def test_nested_methods(parser):
    def echo(x):
        return x

    parser.methods.update({
        'echo': echo
    })
    parser.expr.update({
        'test': '$delimitedList[$echo[number]]',
    })

    c = parser.compile()
    assert list(c['test'].parseString('1,42,3,4')) == [1, 42, 3, 4]


def test_method_and_name(parser):
    def echo(x):
        return x

    parser.methods.update({
        'echo': echo
    })
    parser.expr.update({
        'test': '@me:$echo[number]',
        'test2': '@me:($echo[number])',
    })

    c = parser.compile()
    assert c['test'].parseString('42')['me'] == 42
    assert c['test2'].parseString('42')['me'] == 42


def test_method_and_more(parser):
    def echo(x):
        return x

    parser.methods.update({
        'echo': echo
    })
    parser.expr.update({
        'test': '@me:$echo[number] @name:(identifier | /&+/)',
    })

    c = parser.compile()
    assert c['test'].parseString('42 &&&&&&&&&&')['name'] == '&&&&&&&&&&'
    assert c['test'].parseString('42 alvaro')['name'] == 'alvaro'


def test_method_as_argument(parser):
    def echo(x):
        return x

    def appl(x, *y):
        return x(*y)

    parser.methods.update({
        'echo': echo,
        'appl': appl,

    })
    parser.expr.update({
        'test': '$appl[$echo,number]',
    })

    c = parser.compile()
    assert c['test'].parseString('42')[0] == 42


def test_decorator(parser):
    @parser.method
    def echo(x):
        return x

    @parser.method
    def appl(x, *y):
        return x(*y)

    assert parser.methods['echo'] == echo
    assert parser.methods['appl'] == appl

    parser.expr.update({
        'test': '$appl[$echo, number]',
    })

    c = parser.compile()
    assert c['test'].parseString('42')[0] == 42
