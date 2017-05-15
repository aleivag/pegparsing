
status = """/10.1.2.4
  generation:0
  heartbeat:0
/10.1.2.3
  generation:0
  heartbeat:0
/10.1.2.6
  generation:1444263348
  heartbeat:6232
  LOAD:2.0293227179E10
  INTERNAL_IP:10.26.81.97
  DC:DC1
  STATUS:NORMAL,-1041938454866204344
  HOST_ID:36fdcf57-0274-43b8-a501-c0e475e3e30b
  X_11_PADDING:{"workload":"Cassandra","active":"true"}
  RPC_ADDRESS:10.26.81.97
  RACK:RAC1
  SCHEMA:ce2a34e3-0967-34ea-ad55-10270b805218
  NET_VERSION:7
  RELEASE_VERSION:2.0.12.275
  SEVERITY:0.0
/10.1.2.5
  generation:0
  heartbeat:0"""

def test_goosip_info(parser):


  parser.expr.update({
    'hostinfostart': '"/"! (ipv4_address | ipv6_address )',
  
    'number_headers': "'NET_VERSION' | 'LOAD' | 'SEVERITY' | 'generation' | 'heartbeat' ",
    'num_values': ('" "*! number_headers ":"! number ', lambda r: [r]),
  
    'df': (r'" "*! identifier ":"! /.+/ ', lambda r: [r]),
  
    'kv': 'num_values | df'
  })

  @parser.peg('hostinfostart kv+')
  def gossiphostinfo(result):
    return {result[0]: {r[0]: r[1] for r in result[1:]}}

  @parser.peg('gossiphostinfo+')
  def gossipinfo(result):
    return {k: v for r in result for k,v in r.items()}

  #c = parser.compile()
  goosip_parsed = gossipinfo.parseString(status)[0]
  assert set(goosip_parsed) == set(["10.1.2.4", "10.1.2.3", "10.1.2.6", "10.1.2.5"])
  assert goosip_parsed['10.1.2.6']['LOAD'] == 2.0293227179E10
  