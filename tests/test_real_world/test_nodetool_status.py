
status = """Datacenter: r1
==============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
-- Address Load Tokens Owns Host ID Rack\
DN 10.1.2.5 ? 256 9.0% 5279619a-550c-42b3-8150-61ad24f828f3 r1
DN 10.1.2.3 0 gb 256 9.1% 5d1fa459-cdac-4658-b68d-c6e0933afcee r1
DN 10.1.2.4 0 gb 256 10.5% a8f35c63-6a76-4e95-99f1-bef65d785366 r1
Datacenter: DC1
===============
Status=Up/Down
|/ State=Normal/Leaving/Joining/Moving
-- Address Load Tokens Owns Host ID Rack\
UN 10.1.2.6 18.9 gb 256 9.5% 36fdcf57-0274-43b8-a501-c0e475e3e30b RAC1"""


def test_nodetol_status_parser(report, parser):
    sizec = {'k': 1024, 'm': 1024**2, 'g': 1024**3}
    parser.expr.update({
        'state': "/[UD]/",
        'status': "/[NLJM]/",
        'byte_sizes_unit': ('/[gGmMkK]/ /[bB]/', lambda x: sizec.get(x[0])),
        'uid': '/[a-f0-9-]+/',
        'h1': '/=/+',
        'h2': '"Status=Up/Down"!',
        'h3': "'|/ State=Normal/Leaving/Joining/Moving'",
        'h4': "'--' 'Address' 'Load' 'Tokens' 'Owns' 'Host ID' 'Rack'",
        'dch': "'Datacenter:'! identifier",
    })

    @parser.peg("(number byte_sizes_unit) | '?'   ")
    def bsize(result):
        if result[0] == '?':
            return '?'
        return result[0] * result[1]

    @parser.peg("state status ipv4_address bsize number (number '%'!) uuid identifier")
    def line(result):
        return {
            'state': {'U': 'Up', 'D': 'Down'}.get(result[0]),
            'status': {"N": "Normal", "L": "Leaving", "J": "Joining", "M": "Moving"}[result[1]],
            'Address': result[2],
            'load': result[3],
            'tokens': result[4],
            'own': result[5],
            'host_id': result[6],
            'rack': result[7]
        }

    @parser.peg('dch (h1 h2 h3 h4)! line+')
    def dc(result):
        return (result[0], result[1:])

    @parser.peg('dc+')
    def dcs(result):
        return {k: v for k, v in result}

    with report.create_timer('compile'):
        c = parser.compile()

    out = c['dcs'].parseString(status)[0]

    assert set(out.keys()) == set(['r1', 'DC1'])
    assert len(out['r1']) == 3
    assert len(out['DC1']) == 1

    with report.create_timer('direct_call'):
        out = dcs.parseString(status)[0]

    assert set(out.keys()) == set(['r1', 'DC1'])
    assert len(out['r1']) == 3
    assert len(out['DC1']) == 1


def test_nodetol_status_better_parser(report, parser):
    sizec = {'k': 1024, 'm': 1024**2, 'g': 1024**3}
    parser.expr.update({
        'state': "/[UD]/",
        'status': "/[NLJM]/",
        'byte_sizes_unit': ('/[gGmMkK]/ /[bB]/', lambda x: sizec.get(x[0])),
        'h1': '/=+/',
        'h2': '"Status=Up/Down"!',
        'h3': "'|/ State=Normal/Leaving/Joining/Moving'",
        'h4': "'--' 'Address' 'Load' 'Tokens' 'Owns' 'Host ID' 'Rack'",
        'dch': "'Datacenter:'! identifier",
    })

    @parser.peg("(number byte_sizes_unit) | '?'   ")
    def bsize(result):
        if result[0] == '?':
            return '?'
        return result[0] * result[1]

    @parser.peg("state status ipv4_address bsize number (number '%'!) uuid identifier")
    def line(result):
        return {
            'state': {'U': 'Up', 'D': 'Down'}.get(result[0]),
            'status': {"N": "Normal", "L": "Leaving", "J": "Joining", "M": "Moving"}[result[1]],
            'Address': result[2],
            'load': result[3],
            'tokens': result[4],
            'own': result[5],
            'host_id': result[6],
            'rack': result[7]
        }

    @parser.peg('dch (h1 h2 h3 h4)! line+')
    def dc(result):
        return (result[0], result[1:])

    @parser.peg('dc+')
    def dcs(result):
        return {k: v for k, v in result}

    with report.create_timer('compile'):
        c = parser.compile()

    out = c['dcs'].parseString(status)[0]

    assert set(out.keys()) == set(['r1', 'DC1'])
    assert len(out['r1']) == 3
    assert len(out['DC1']) == 1

    with report.create_timer('direct_call'):
        out = dcs.parseString(status)[0]

    assert set(out.keys()) == set(['r1', 'DC1'])
    assert len(out['r1']) == 3
    assert len(out['DC1']) == 1
