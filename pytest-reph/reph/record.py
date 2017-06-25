from datetime import datetime

from reph.timer import Timer


class ReportRecord(object):
    @property
    def session_id(self):
        return self.store.session_id

    def __init__(self, nodeid, store):
        self.nodeid = nodeid
        self.store = store
        self.start_time = datetime.utcnow()
        self.stop_time = None

        self.stage = {
            'setup': {},
            'call': {},
            'teardown': {},
        }
        self.timers = []

    def flush(self):
        self.store.commit_row(self)

    def set_stage_information(self, stage, information):
        self.stage[stage].update(information)
        for k, v in information.items():
            setattr(self, 'stage_%s_%s' % (stage, k), v)

    def create_timer(self, name):
        t = Timer(name)
        self.timers.append(t)
        return t
