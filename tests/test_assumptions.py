import pyparsing
from pegparsing import get_pyparsing

class FakePyParsing(object):
    ParserElement=True

def test_importer():
    
    ma1 = get_pyparsing('ma')
    ma2 = get_pyparsing('ma')
    mb0 = get_pyparsing('mb')
    original = get_pyparsing(None)
    fake = get_pyparsing(FakePyParsing)
    
    assert id(ma1) == id(ma2)
    assert id(ma1) != pyparsing
    
    assert id(ma2) != id(mb0)
    
    assert original == pyparsing
    
    assert fake == FakePyParsing
    
    
    


    