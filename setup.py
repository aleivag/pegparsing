import os
from distutils.core import setup

from pegparsing import __version__

try:
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        long_description = f.read()
except:
    long_description = ''

setup(
    name='pegparsing',
    version=__version__,
    packages=['pegparsing'],
    author='Alvaro Leiva',
    author_email='aleivag@gmail.com',
    url='https://gitlab.com/aleivag/pegparsing',
    classifiers=[
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    keywords=['parsing'],
    description='a peg interface to pyparsing',
    long_description=long_description,
    license='MIT'
)