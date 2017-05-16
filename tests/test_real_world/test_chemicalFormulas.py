
class Element(object):
    def __init__(self, name, w):
        self.name = name
        self.w = w


atomicWeight = {
    "O": Element('O', 15.9994),
    "H": Element('H', 1.00794),
}

caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowers = caps.lower()
digits = "0123456789"


def test_chemicalFormulas(parser):
    parser.expr.update({
        'element': parser.pubparser.Word(caps, lowers),
        'one_element_molecule': ('element integer?', lambda x: tuple(x)),
        'molecule': 'one_element_molecule+'
    })

    c = parser.compile()
    assert list(c['molecule'].parseString('H2O')) == [('H', 2), ('O', )]
    assert list(c['molecule'].parseString('NaCl')) == [('Na', ), ('Cl', )]
    assert list(c['molecule'].parseString('HOCH2CH')) == [
        ('H', ), ('O', ), ('C', ), ('H', 2), ('C', ), ('H', )]
