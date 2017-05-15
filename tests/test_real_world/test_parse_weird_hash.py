from __future__ import print_function

def test_weird_hash(parser):
    
    parser.expr.update({
        'key': 'number ',
        'value': 'hash | key',
        'kv': ('key "=>"! value ', lambda r: (r[0], r[1])),
        'kvs': '$delimitedList[kv]',
    })
    
    @parser.peg(' "{"! kvs "}"! ')
    def hash(result):
        return {k:v for k,v in result}
    
    compiled = parser.compile()
    
    assert compiled['hash'].parseString('{ 3 => 9, 4 => {1 => 2 } }')[0] == \
        {3: 9, 4: {1: 2}}