import uuid
from datetime import datetime
import pytest

from reph.stores import REPORT_STORES
from reph.stores.base_store import ReportStore
from reph.record import ReportRecord


def pytest_addoption(parser):
    parser.addoption("--session-id", action="store",
                     default=str(uuid.uuid4()),
                     help="specify this to ensure the same session between "
                     "multiple executions.")

    parser.addoption("--report-store", action="store", default=None,
                     help="the store detination of report, "
                     "leave blank to dont store")


@pytest.fixture(scope='session', autouse=True)
def report_store(request):
    store_uri = pytest.config.getoption('report_store')
    session_id = pytest.config.getoption('session_id')

    # TODO: parse the url and make a direct get to the STORE DICT
    if store_uri is None:
        request.session.report_store = ReportStore(store_uri, session_id)
    else:
        for k, v in REPORT_STORES.items():
            if store_uri.startswith(k + '://'):
                request.session.report_store = v(store_uri, session_id)
                break
        else:
            raise NotImplementedError('No store for %s' % store_uri)

    yield request.node.report_store

    request.session.report_store.mark_as_ready_to_commit()


@pytest.fixture(autouse=True, ids='report')
def report(request, report_store):
    request.node.report = ReportRecord(request.node.nodeid, store=report_store)
    report_store.add_row(request.node.report)
    yield request.node.report
    request.node.report.stop_time = datetime.utcnow()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    item.report.set_stage_information(rep.when, {
        'duration': rep.duration,
        'outcome': rep.outcome
    })

    if rep.when == 'teardown':
        item.report.flush()
        if item.report.store.ready_to_commit:
            item.report.store.commit()
