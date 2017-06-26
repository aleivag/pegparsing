"""
Call script with

venv2.sh anareph.py tests.db test_reporting master

or

venv3.sh anareph.py tests.db test_reporting master

"""

import sys
import sqlite3

from itertools import groupby
from terminaltables import AsciiTable


FILE = sys.argv[1]
COMA = sys.argv[2]
COMB = sys.argv[3]

QUERY_ALL_TEST_RESULTS = """
SELECT
    id, nodeid, stage_setup_duration,
    stage_call_duration, stage_teardown_duration
FROM TestResult
WHERE session_id = :session_id
"""

QUERY_TIMERS_PER_TEST_RESULTS = """
SELECT timer_name, duration
FROM TestTimer
where test_result_id = :test_result_id
"""

conn = sqlite3.connect(FILE)
c = conn.cursor()

branches = {}

for branch in sys.argv[2:]:
    c.execute("""

SELECT session_id, value, Session.start
FROM Tag INNER JOIN Session ON Session.id = Tag.session_id
where session_id in (
    SELECT session_id
    FROM Tag
    WHERE key='git_banch' and value = :branch
) AND
    key = 'python_version_mayor'

""", {'branch': branch})
    records = c.fetchall()
    records.sort(key=lambda x: x[1])
    branches[branch] = {}
    for pversion, rec in groupby(records, key=lambda x: x[1]):
        srec = list(sorted(rec, key=lambda x: x[2], reverse=True))[0]
        branches[branch][pversion] = {
            'session_id': srec[0], 'start': srec[2],
            'tests': {}
        }

        c.execute(QUERY_ALL_TEST_RESULTS, (srec[0],))
        branches[branch][pversion]['tests'] = {
            row[1]: {
                'stage_setup_duration': row[2],
                'stage_call_duration': row[3],
                'stage_teardown_duration': row[4],
                'timers': {
                    timer[0]: timer[1]
                    for timer in c.execute(
                        QUERY_TIMERS_PER_TEST_RESULTS,
                        {'test_result_id': row[0]})
                }
            }
            for row in c.fetchall()
        }


all_pythons = sorted(list({k for v in branches.values() for k in v}))
all_tests = sorted(list({
    test
    for branchv in branches.values()
    for pyv in branchv.values()
    for test in pyv.get('tests', {})
}))

PYV = ' / '.join(all_pythons)

rows = [
    ['branch', 'setup\n%s' % PYV, 'call\n%s' % PYV, 'teardown\n%s' % PYV]
]

for branch in branches:
    PYT = {'setup': [], 'call': [], 'teardown': []}
    for pyv in all_pythons:
        tests = branches[branch].get(pyv, {'tests': {}}).get('tests', {})
        PYT['setup'].append(
            '%.1f' % sum(v['stage_setup_duration'] for v in tests.values()))
        PYT['call'].append(
            '%.1f' % sum(v['stage_call_duration'] for v in tests.values()))
        PYT['teardown'].append(
            '%.1f' % sum(v['stage_teardown_duration'] for v in tests.values()))

    rows.append([
        branch,
        ' / '.join(PYT['setup']),
        ' / '.join(PYT['call']),
        ' / '.join(PYT['teardown']),
    ])

print('-' * 80)
print('quick pversion summary')
table = AsciiTable(rows)
print(table.table)
print('-' * 80)
print('\n\n')


# TEST SUMMARY

BRT = ' / '.join(branches)

rows = [
    ['Test'] + ['py%s\n%s' % (pyv, BRT) for pyv in all_pythons]
]

for test in all_tests:
    row = [test]
    all_timers = {
        timer
        for branch in branches
        for pyv in all_pythons

        for timer in branches[branch].get(
                pyv, {}
            ).get('tests', {}).get(
                test, {}).get('timers', {})
    }

    for pyv in all_pythons:
        row.append(' / '.join(
            '%.2f' % branches[branch].get(
                pyv, {}
            ).get('tests', {}).get(
                test, {}
            ).get('stage_call_duration', 0)
            for branch in branches
        ))

    rows.append(row)
    for timer in all_timers:
        trow = [' \\--> %s' % timer]
        for pyv in all_pythons:
            trow.append(
                ' / '.join(
                    '    %.2f' % branches[branch].get(
                            pyv, {}
                        ).get('tests', {}).get(test, {}).get(
                            'timers', {}
                        ).get(timer, 0)
                    for branch in branches
                )
            )

        rows.append(trow)


print('-'*80)
print('quick Test summary')
table = AsciiTable(rows)
print(table.table)
print('-'*80)
print('\n\n')
