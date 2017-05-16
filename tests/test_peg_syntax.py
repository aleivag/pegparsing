
import pytest


def test_add(parser):
    parser.expr.update({
        "str1": "'str1'",
        "str2": '"str2"',
        "regx": '/\d+/',
        "comb": 'str1   str2   regx'
    })
    comb = parser.compile()['comb']
    assert list(comb.parseString('str1 str2 42')) == ['str1', 'str2', '42']
    assert list(comb.parseString('    str1     str2     42   ')) == \
        ['str1', 'str2', '42']
    assert list(comb.parseString('str1str242')) == \
        ['str1', 'str2', '42']


def test_or(parser):
    parser.expr.update({
        "str1": "'str1'",
        "str2": '"str2"',
        "regx": '/\d+/',
        "comb": 'str1 |  str2  | regx'
    })
    comb = parser.compile()['comb']
    assert comb.parseString('str1')[0] == 'str1'
    assert comb.parseString('str2')[0] == 'str2'
    assert comb.parseString('42')[0] == '42'


def test_parentesis(parser, pyparsing):
    parser.expr.update({
        "str1": "'str1'",
        "str2": '"str2"',
        "regx": '/\d+/',
        "combA": '(str1 |  str2)   regx',
        "combB": 'str1   (str2  | regx)'
    })
    c = parser.compile()

    assert list(c['combA'].parseString('str1 42')) == ['str1', '42']
    assert list(c['combA'].parseString('str2 42')) == ['str2', '42']

    assert list(c['combB'].parseString('str1 42')) == ['str1', '42']
    assert list(c['combB'].parseString('str1 str2')) == ['str1', 'str2']

    with pytest.raises(pyparsing.ParseException):
        c['combA'].parseString('str1 str2 42')
        c['combA'].parseString('str1 str2')

        c['combB'].parseString('str1 str2 42')
        c['combB'].parseString('str2 42')


def test_suppression(parser):
    parser.expr.update({
        "str1": "'str1'",
        "str2": '"str2"',
        "regx": '/\d+/',
        "comb": ' str1!  regx',
    })

    c = parser.compile()
    assert c['comb'].parseString('str1 42')[0] == '42'


def test_naming(parser):
    parser.expr.update({
        "str1": "'str1'",
        "str2": '"str2"',
        "regx": '/\d+/',
        "comb": ' @head:str1  @tail:regx',
    })

    c = parser.compile()
    assert dict(c['comb'].parseString('str1 42')) == {'head': 'str1', 'tail': '42'}
