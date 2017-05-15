
import fnmatch

name_l = {
    'james': ['taylor', 'brown'],
    'neil': ['young', 'diamond'],
}

def test_group_p(parser):
    
    parser.expr['ooo'] = r'/[\w\*]+/'
    
    @parser.peg(r'/[\w\*]+/')
#    @parser.peg(r' ooo ')
    def first_name(result):
        return set(fnmatch.filter(name_l, result[0]))
    
    @parser.peg(r'@fname:first_name @lname:ooo')
    def full_name(result):
        return {
            (fname, lname) 
            for fname in result['fname'] 
            for lname in name_l[fname] 
            if fnmatch.fnmatch(lname, result['lname'])
        
        }
    
    assert first_name.parseString('jam*')[0] == {'james'}
    assert full_name.parseString('* b*')[0] == {
        ('james', 'brown')
    }
    assert full_name.parseString('* *')[0] == {
        (k, v) for k in name_l for v in name_l[k]
    }
    