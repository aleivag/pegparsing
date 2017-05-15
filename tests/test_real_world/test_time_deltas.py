
from datetime import datetime, timedelta

DELTAS = {
    'w': timedelta(days=7),
    'd': timedelta(days=1),
    'h': timedelta(seconds=60*60),
    'm': timedelta(seconds=60),
    's': timedelta(seconds=1),
}

OP = {
    '+': lambda x,y: x+y,
    '-': lambda x,y: x-y,
}

def test_dtime(parser):
    
    now = datetime.now()
    
    parser.expr.update({
        'time_unit': (
            '/[wdhms]/', 
            lambda x: DELTAS[x[0]]),
        'delta_time': (
            'integer time_unit', 
            lambda x: x[0] * x[1])
    })
    
    @parser.peg(' "now" | "tomorrow" | "yesterday" ')
    def base_time(result):
        # on a real code (not test), you may want to set as below VVV
        #now = datetime.now()
        if result[0] == 'now':
            delta = timedelta(seconds=0)
        elif result[0] == 'tomorrow':
            delta = DELTAS['d']
        elif result[0] == 'yesterday':
            delta = -DELTAS['d']
        
        return now + delta
    
    @parser.peg('@base:base_time @deltas:(/[+-]/ delta_time)*')
    def time_expr(result):
        left = result['base']
        while result.get('deltas'):
            op, right = result['deltas'].pop(0), result['deltas'].pop(0)
            left = OP[op](left, right)
        return left
    
    assert time_expr.parseString('now')[0] == now
    assert time_expr.parseString('now + 1d')[0] == now + timedelta(1)
    assert time_expr.parseString('now + 1w - 1w')[0] == now
    
    assert time_expr.parseString('yesterday')[0] == time_expr.parseString('now - 1d')[0] 
    assert time_expr.parseString('yesterday + 1d')[0] == time_expr.parseString('now')[0] 
    assert time_expr.parseString('yesterday + 2d')[0] == time_expr.parseString('tomorrow')[0] 
    assert time_expr.parseString('yesterday')[0] == time_expr.parseString('tomorrow-2d')[0] 
    assert time_expr.parseString('now')[0] == time_expr.parseString('tomorrow-1d')[0] 
    assert time_expr.parseString('now + 1d')[0] == time_expr.parseString('tomorrow')[0] 
    
    