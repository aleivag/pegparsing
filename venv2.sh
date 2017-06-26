#!/bin/bash


vdir=$(mktemp -d)

virtualenv ${vdir}

${vdir}/bin/pip install -r requirements.txt > /dev/null
${vdir}/bin/python setup.py install > /dev/null

source ${vdir}/bin/activate

ipython "$@"

deactivate

rm -rf ${vdir}
