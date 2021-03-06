
vdir=$(mktemp -d)

virtualenv --python=/usr/bin/python3.5 ${vdir} > /dev/null

${vdir}/bin/pip install -r requirements.txt > /dev/null
${vdir}/bin/python setup.py install > /dev/null
${vdir}/bin/pip install -r requirements-test.txt > /dev/null

cd pytest-reph; ${vdir}/bin/python setup.py install >/dev/null ; cd -

${vdir}/bin/pytest -s tests/ "$@"


rm -rf ${vdir}