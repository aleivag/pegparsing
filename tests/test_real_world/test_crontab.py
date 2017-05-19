CRONTAB = """

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# and this is another comment

17 *    * * *   root    cd / && run-parts --report /etc/cron.hourly
25 6    * * *   ubuntu    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )


# this is a comment

52 6    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )


52 6    1 * *   aleivag    libuntu -x localhost -p s3ntr1

""".strip()


class Crontab(object):
    def __init__(self):
        self.variables = {}
        self.cronline = []


def test_crontab(parser):

    ct = Crontab()

    parser.expr.update({
        'comment': '/#.*/'
    })

    @parser.peg('identifier "="! /.+/')
    def vars_assig(result):
        ct.variables[result[0]] = result[1]
        return [list(result)]

    @parser.peg('(integer | "*") ("/" integer)?')
    def number_or_star(result):
        return result[0]

    @parser.peg(
        '@min:number_or_star @hour:number_or_star '
        '@dom:number_or_star @month:number_or_star '
        '@dow:number_or_star @user:identifier @cmd:/.+/')
    def cronline(result):
        ct.cronline.append(dict(result))
        return ct.cronline[-1]

    @parser.peg('(vars_assig | cronline | comment!)+')
    def crontab(result):
        return list(result)

    parsed = crontab.parseString(CRONTAB)

    assert ct.variables == {
        'PATH': '/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin',
        'SHELL': '/bin/sh'
    }
    assert len(parsed) == 7
    assert set(x['user'] for x in ct.cronline) == set(['ubuntu', 'root', 'aleivag'])
