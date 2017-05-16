
vdir=$(mktemp -d)

virtualenv ${vdir} > /dev/null

${vdir}/bin/pip install -r requirements.txt > /dev/null
${vdir}/bin/python setup.py install > /dev/null
${vdir}/bin/pip install -r requirements-test.txt > /dev/null
${vdir}/bin/py.test -s tests/ "$@"
${vdir}/bin/flake8 pegparsing/ tests/ --ignore=E501


rm -rf ${vdir}