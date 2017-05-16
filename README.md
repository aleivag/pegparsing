# Pegparsing


`pegparsing` is a library that allows you to parse text, by writing pseudo-PEG expressions. 
Under the covers `pegparsing` will translate the peg instruction and allow the 
text to be processed by [pyparsing](http://pyparsing.wikispaces.com/), you dont 
have to know or care about that.

![travis-status](https://api.travis-ci.org/aleivag/pegparsing.svg?branch=master)

Example use:
------------

You need to turn something like `{ 3 => 9, 4 => {1 => 2 } }` to a python 
dictionary, it consist of comma-delimited key/value enclosed by brackets, where a 
key can be an integer and value can be either an integer or another hash structure.


```python
from pegparsing import Parser

parser = Parser()

parser.expr.update({
    'key': '/\d+/',
    'value': 'hash | key',
    'kv': ('key "=>"! value ', lambda r: (r[0], r[1])),
    'kvs': '$delimitedList[kv]',
})

@parser.peg(' "{"! kvs "}"! ')
def hash(result):
    return {k:v for k,v in result}
    
compiled = parser.compile()
print(
    compiled['hash'].parseString('{ 3 => 9, 4 => {1 => 2 } }')[0]
)

```

This will output:

    {3: 9, 4: {1: 2 }}

Hands on tutorial:
--------------------------

Let's create a simple parser that can understand dates in terms of `now + 1w` or 
`tomorrow + 1d - 10m`. This is how the code will look like:

```python

from datetime import datetime, timedelta

from pegparsing import Parser

parser = Parser()

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

parser.expr.update({
    'time_unit': ('/[wdhms]/', lambda x: DELTAS[x[0]]),
    'delta_time': ( 'integer time_unit', lambda x: x[0] * x[1])
})

@parser.peg(' "now" | "tomorrow" | "yesterday" ')
def base_time(result):
    now = datetime.now()
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
    while result['deltas']:
        op, right = result['deltas'].pop(0), result['deltas'].pop(0)
        left = OP[op](left, right)
    return left

print(time_expr.parseString('now')[0])
print(time_expr.parseString('now + 1w')[0])
print(time_expr.parseString('yesterday - 7d')[0])

```

Let’s begin. The first expression that we want to be able to parse, 
is the absolute (or base) time. we are going to keep it simple, and  just allow `now` `yesterday` and `tomorrow`. 

In `pegparsing` you start by creating a `parser` and then creating tokens in `parser.expr` dict.

```python
>>> from pegparsing import Parser
>>> parser = Parser()
>>> parser.expr['base_time'] = ' "now" | "tomorrow" | "yesterday" '
>>> parser.expr['base_time']
' "now" | "tomorrow" | "yesterday" '
``` 

Now `base_time` is defined as the literal word "now", "tomorrow" or "yesterday".
The `|` means the OR operand. Let’s see it in action.

    
```python

>>> compile = parser.compile()
>>> compile['base_time'].parseString('now')
(['now'], {})

>>> yesterday = compile['base_time'].parseString('yesterday')
>>> yesterday
(['yesterday'], {})

>>> yesterday[0]
'yesterday'

```

As you can see you can parse strings (using the method parseString… crazy right) 
after you compile your parser, 
and you’ll get a weird looking result. Don’t be afraid of the result, 
it may look like a weird tuple of a list and a dict `([], {})`, but its not, is an object 
that acts like a list and a dict... more on this later, just 
notice that `yesterday[0]` returned `'yesterday'` and not `['yesterday']`.

Now if the parser can’t parse the expression you gave it, you'll get a error… granted it’s not the best error, we are working on it, let’s first have a functional parser, ok mate.

```
>>> compile['base_time'].parseString('last year')
---------------------------------------------------------------------------
ParseException                            Traceback (most recent call last)
<ipython-input-12-6311beccd571> in <module>()
----> 1 yesterday = compile['base_time'].parseString('last year')

/tmp/tmp.LbOLJgwsOY/lib/python2.7/site-packages/pyparsing.pyc in parseString(self, instring, parseAll)
   1630             else:
   1631                 # catch and re-raise exception from here, clears out pyparsing internal stack trace
-> 1632                 raise exc
   1633         else:
   1634             return tokens

ParseException: Expected {"now" | "tomorrow" | "yesterday"} (at char 0), (line:1, col:1)
```

Ok, so far so good, but you can do the same thing with regex, so... why the bother at all with this. 
Well parsing has 2 steps, the lexer (what you actually just did), and the parser (some call this compiler, i don’t like that term), that means that after you got your match, you can associate an action in a nice simple (if you don’t mind me saying so) and pythonic way. So let’s re define the token `base_time`.


```python

>>> from datetime import datetime, timedelta
>>> @parser.peg(' "now" | "tomorrow" | "yesterday" ')
... def base_time(result):
...     now = datetime.now()
...     if result[0] == 'now':
...         delta = timedelta(seconds=0)
...     elif result[0] == 'tomorrow':
...         delta = timedelta(days=1)
...     elif result[0] == 'yesterday':
...         delta = -timedelta(days=1)
...     return now + delta

>>> compile = parser.compile()
>>> compile['base_time'].parseString('now')
([datetime.datetime(2017, 5, 3, 3, 28, 39, 339375)], {})

```

So you can process a parsing structure by decorating a function (the function 
name is now the token name), the function accept the original parsing result
and return a new value, this can be anything, from string to classes, whatever
you want. And just in case you were wondering what 
does `parser.expr['base_time']` now looks like: 

```python
>>> parser.expr['base_time']
(' "now" | "tomorrow" | "yesterday" ', <function __main__.base_time>)
```

almost the same as before, but now instead of just the expression string, is a tuple with the  parsing function as the second element.

So that is all i have to say about that. Now let’s move to the deltas. Deltas are string in the form of `1w` or `30d`, a unit and a length, the final expression should be something like `unit * length`. 

So we first parse the letter, we can clearly build a simple dict like

```python
>>> DELTAS = {
    'w': timedelta(days=7),
    'd': timedelta(days=1),
    'h': timedelta(seconds=60*60),
    'm': timedelta(seconds=60),
    's': timedelta(seconds=1),
}
```

To use it we could create something like '"w" | "d" | ...' but is text 
comparison, there is a better way:

```python
>>> @parser.peg('/[wdhms]/'),
... def time_unit(resp):
...     return DELTAS[resp[0]]

>>> time_unit.parseString('w')
timedelta(7)
```

Using `/[wdhms]/`, that is a regular expression. so regular expression are 
"forward slash quoted strings" or whatever you want to write between `/`.

The resulting `time_unit` function is really small, basically a one liner 
and in that case decorating a small function may be a overkill, 
so you can translate the `time_unit` token to something shorter like

```python
>>> parser.expr['time_unit'] = ('/[wdhms]/', lambda x: DELTAS[x[0]])
>>> c = parser.compile()
>>> c['time_unit'].parseString('w')
timedelta(7)
```

so if you add a tuple to `parser.expr[<name>]` the first element will be the 
parse expression, and the second one will be the parse function. 

A `delta_time` is something that should take `2w` and return `timedelta(14)` (14 days). This will do the trick:

```python
>>> parser.expr['delta_time'] = ( '/\d+/ time_unit', lambda x: x[0] * x[1] )
>>> c = parser.compile()
>>> c['delta_time'].parseString('2w')
timedelta(14)
```

Its simple, basically a number `/\d+/` and then the `time_unit` token that we 
already defined. Now one of my ideas while doing this library was to have as many 
"batteries included" as reasonable, and having a `integer` token seems logic 
(you could look at `parser.expr` and inspect what other free tokens you get).

```python
>>> parser.expr['delta_time'] = ( 'integer time_unit', lambda x: x[0] * x[1] )
>>> c = parser.compile()
>>> c['delta_time'].parseString('2w')[0]
timedelta(14)
>>> c['delta_time'].parseString('-2w')[0]
timedelta(-14)
```

The last 2 expressions can be just combined into a single statement like this.

```python
>>> parser.expr.update({
    'time_unit': ('/[wdhms]/', lambda x: DELTAS[x[0]]),
    'delta_time': ( 'integer time_unit', lambda x: x[0] * x[1])
})
```

The final part is simple, now we have something that can parse reference time, 
like `now` and something that can parse delta times like `2d`. We could do 
something like this:


```python
>>> parser.expr['time_expr'] = ('base_time "+"! delta_time')
>>> c = c = parser.compile()
>>> c['time_expr'].parseString('now + 2d')
([datetime.datetime(2017, 5, 6, 14, 56, 4, 708785), timedelta(2)], {})
```

So `base_time "+"! delta_time` try to parse a `base_time` follow by the literal 
`"+"` sign but the `!` means that if should not return that token, and then follow
by a `delta_time`. this has the disadvantage that will only parse stuff like `yesterday + 1w`
but not just `yesterday`. Let’s fix that

```python
>>> parser.expr['time_expr'] = ('base_time ("+"! delta_time)?')
>>> c = c = parser.compile()
>>> c['time_expr'].parseString('now + 2d')
([datetime.datetime(2017, 5, 6, 14, 56, 4, 708785), timedelta(2)], {})
>>> c['time_expr'].parseString('now')
([datetime.datetime(2017, 5, 6, 14, 56, 4, 708785)], {})
```

the familiar `("+"! delta_time')?` means that the expression is optional. Now 
how about we may want to add more than just delta, and parse stuff like  
`yesterday + 1w + 3d`, lets try


```python
>>> parser.expr['time_expr'] = ('base_time ("+"! delta_time')*)
>>> c = c = parser.compile()
>>> c['time_expr'].parseString('now + 2d')
([datetime(2017, 5, 6, 14, 56, 4, 708785), timedelta(2)], {})
>>> c['time_expr'].parseString('now + 2d + 1d')
([datetime(2017, 5, 6, 14, 56, 4, 708785), timedelta(2), timedelta(1)], {})
>>> c['time_expr'].parseString('now')
([datetime(2017, 5, 6, 14, 56, 4, 708785)], {})
```

The familiar `("+"! delta_time')*` means zero or more. this seems good so far. Since 
now we can have zero or more deltas we need to take the `base_time` and add to it
as many `delta_time` as passed. lets use a feature that is really cool on our 
framework, and that is named expressions, they work like this:

```python
>>> parser.expr['time_expr'] = '@base:base_time @deltas:("+"! delta_time)*'
>>> c = parser.compile()
>>> p = c['time_expr'].parseString('now + 2d +6w')
>>> p
([datetime(2017, 5, 6, 14, 56, 4, 708785), datetime.timedelta(2), datetime.timedelta(42)], {'deltas': [([datetime.timedelta(2), datetime.timedelta(42)], {})], 'base': [datetime(2017, 5, 6, 14, 56, 4, 708785)]})
>>> p[0]
datetime(2017, 5, 6, 14, 56, 4, 708785)
>>> p['base']
datetime(2017, 5, 6, 14, 56, 4, 708785)
>>> p[0] == p['base']
True
```

Now you can refer to specific parts by name. Now let’s actually parse and process 
the expression, but let’s also allow for subtraction of deltas, like this:


```python
>>> OP = {
    '+': lambda x,y: x+y,
    '-': lambda x,y: x-y,
}

>>> @parser.peg('@base:base_time @deltas:(/+-/! delta_time)*')
... def time_expr(result):
...     left = result['base']
...     while result['deltas']:
...         op, right = result['deltas'].pop(0), result['deltas'].pop(0)
...         left = OP[op](left, right)
...     return left
>>> time_expr.parseString('now + 1d')[0]
datetime(2017, 5, 7, 14, 56, 4, 708785)
```

And now just put everything together:

```python

from datetime import datetime, timedelta

from pegparsing import Parser

parser = Parser()

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

parser.expr.update({
    'time_unit': ('/[wdhms]/', lambda x: DELTAS[x[0]]),
    'delta_time': ( 'integer time_unit', lambda x: x[0] * x[1])
})

@parser.peg(' "now" | "tomorrow" | "yesterday" ')
def base_time(result):
    now = datetime.now()
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
    while result['deltas']:
        op, right = result['deltas'].pop(0), result['deltas'].pop(0)
        left = OP[op](left, right)
    return left
```

Parsing Rules
=============

Token types:
------------

* **Literal string**: Just a single (`'`) or double (`"`) quoted string, whatever is inside will 
have to be match completely, including caps

```python
from pegparsing import Parser

parser = Parser()

@parser.peg(' "hi World" ')
def hello(resp):
    return resp

hello.parseString('hi World') # returns (['hi World'], {})

# the next one will fail
hello.parseString('HI WORLD')
hello.parseString('HI-WORLD')
hello.parseString('HI      WORLD')

```

* **Regular expression**: a forward slash string, following the rules of regular expression
like `/\d+/` will match any digits.

```python
from pegparsing import Parser

parser = Parser()

@parser.peg(r' /(25[012345]|2[01234]\d|1?\d?\d)/ ')
def octet(resp):
    #parse all int less than 255
    return int(resp[0])

octet.parseString('5') # returns ([5], {})
octet.parseString('25') # returns ([25], {})
octet.parseString('125') # returns ([125], {})
octet.parseString('255') # returns ([255], {})

# the next ones will fail and not parse
octet.parseString('-5')
octet.parseString('2 55')
octet.parseString('256')
octet.parseString('567')

```

* **Identifier**: Another token, this follow the rules of a python identifier.
 there are a lot of identifier already build in in the framework.

```python
from pegparsing import Parser

parser = Parser()

@parser.peg(r' /(25[012345]|2[01234]\d|1?\d?\d)/ ')
def octet(resp):
    #parse all int less than 255
    return int(resp[0])

@parser.peg(r' octet "."! octet "."! octet "."! octet')
def ipv4_2integer(resp):
    # resp is now 
    return resp[0]*(256**3) + resp[1]*(256**2) + resp[2]*256 + resp[3]

ipv4_2integer.parseString('10.0.0.1')[0] # returns ~ 167772161
ipv4_2integer.parseString('192. 168. 8 . 168')[0] # returns ~ 3232237736

```

* **Name identifiers** : You can name parts of you tokens by using `@<name>:`, 
 prefix, that what they are easy to identify on your parsing function,.

```python
from pegparsing import Parser

parser = Parser()

@parser.peg(r' @head:number @tail:(","! number)* ')
def comma_separated_number_list(resp):
    # resp is now 
    return [resp['head'] ] + list(resp.get('tail', []))

comma_separated_number_list.parseString('1') # returns ~ [1]
comma_separated_number_list.parseString('192, 160 , 8, 168') # returns ~ [192, 168, 8, 168]

```

Operations:
-----------

* **And** (*`whitespaces`*): If 2 tokens are separated by whitespaces only then 
they both need to match. for instance: 

```python
from pegparsing import Parser

parser = Parser()
parser.expr['greet'] = ' "hello" "world" '

c = parser.compile()

c['greet'].parseString('hello world') # returns ~ ["hello", "world"]

# Will fail and throw exception 

c['greet'].parseString('hello cruel world')
c['greet'].parseString('hello')
```


* **Or** (*`|`*): If 2 tokens are separated by a *pipe* (`|`) any one of them can match.
So `Hello ("world" | "you") ` will match "hello world" or "hello you".

```python
from pegparsing import Parser

parser = Parser()
parser.expr['greet'] = ' ("hello" | "goodbye") "world" '

c = parser.compile()

c['greet'].parseString('hello world') # returns ~ ["hello", "world"]
c['greet'].parseString('goodbye world') # returns ~ ["goodbye", "world"]

```


* **Opional** (*`?`*): If a token has a question mark (`?`) at the end then 
it's presence is optional.

```python
from pegparsing import Parser

parser = Parser()
parser.expr['greet'] = '  "goodbye" "cruel"? "world" '

c = parser.compile()


c['greet'].parseString('goodbye world') # returns ~ ["goodbye", "world"]
c['greet'].parseString('goodbye cruel world') # returns ~ ["goodbye", "cruel", "world"]

```


* **Zero or more** (* `*` *): If a token has a star (`*`) at the end then it can appear none, or infinite number of times.

```python
from pegparsing import Parser

parser = Parser()
parser.expr['num_array'] = ' "["  number ("," number)*  ","? "]" '

c = parser.compile()

c['num_array'].parseString('[1, 3, 4, 56, ]') # returns ~ ["[", 1, ",", 2, ",", 4, ",", 56, ",", "]"]
c['num_array'].parseString('[1, ]') # returns ~ ["[", 1, ",", "]"]
c['num_array'].parseString('[1]') # returns ~ ["[", 1, "]"]

#does not parse

c['num_array'].parseString('[]') 
c['num_array'].parseString('[0 0]') 
c['num_array'].parseString('[0; 0]') 

```

* **One or more** (*`+`*): If a token ends with a plus sign (`+`) then it hast appear at least one time, or infinite number of times.

```python
from pegparsing import Parser

parser = Parser()
parser.expr['num_array'] = ' "["  number ("," number)+  ","? "]" '

c = parser.compile()

c['num_array'].parseString('[1, 3, 4, 56, ]') # returns ~ ["[", 1, ",", 2, ",", 4, ",", 56, ",", "]"]
c['num_array'].parseString('[1, 2]') # returns ~ ["[", 1, ",", 2, "]"]


# Does not parse

c['num_array'].parseString('[]') 
c['num_array'].parseString('[1]')
c['num_array'].parseString('[0 0]') 
c['num_array'].parseString('[0; 0]')

```
* **Ignore** (*`!`*): If a token ends with a exclamation sign (`!`) then will be match but it will not go to the result.

```python
from pegparsing import Parser

parser = Parser()


@parser.peg('  "["! number  (","! number)*  (","? "]")!  ')                                                                                       
def na(r):
    return r

c = parser.compile()

na.parseString('[1, 3, 4, 56, ]') # returns ~ [1, 3, 4, 56]

```