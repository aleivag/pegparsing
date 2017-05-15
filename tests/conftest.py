import pytest

from pegparsing import Parser

@pytest.fixture
def parser():
    return Parser()

@pytest.fixture
def pyparsing(parser):
    return parser.pubparser
    