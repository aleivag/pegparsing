
vdir=$(mktemp -d)

virtualenv ${vdir} > /dev/null

${vdir}/bin/pip install -r requirements.txt > /dev/null
${vdir}/bin/python setup.py install > /dev/null
${vdir}/bin/pip install -r requirements-test.txt > /dev/null 
${vdir}/bin/pytest -s tests/ "$@"

rm -rf ${vdir}