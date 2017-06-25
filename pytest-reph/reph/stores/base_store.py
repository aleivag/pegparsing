import os
import platform


class ReportStore(object):
    def __init__(self, store_uri, session_id):
        self.ready_to_commit = False
        self.session_id = session_id
        self.rows = []
        self.tags = {}
        self.set_initial_tags()

    def set_initial_tags(self):
        mayor, minor, patch = platform.python_version_tuple()
        self.tags.update({
            'python_version_mayor': mayor,
            'python_version_minor': minor,
            'python_version_patch': patch,
        })

        git_branch, git_commit = 'None', ''

        cwd = os.path.normcase(os.getcwd())
        _git_dir = os.path.join(cwd, '.git')

        while not os.path.exists(_git_dir):
            tail, _ = os.path.split(cwd)
            if tail == cwd:
                break
            tail = cwd
            _git_dir = os.path.join(cwd, '.git')
        else:
            try:
                _git_head = os.path.join(_git_dir, 'HEAD')
                with open(_git_head) as head:
                    _, git_branch = head.read().strip().rsplit('/', 1)

                _git_ref = os.path.join(_git_dir, 'refs', 'heads', git_branch)

                with open(_git_ref) as ref:
                    git_commit = ref.read().strip()
            except:
                pass

        self.tags.update({
            'git_banch': git_branch,
            'git_commit': git_commit,
        })


    def mark_as_ready_to_commit(self):
        self.ready_to_commit = True

    def add_row(self, row):
        self.rows.append(row)

    def commit(self):
        pass

    def commit_row(self, row):
        pass
