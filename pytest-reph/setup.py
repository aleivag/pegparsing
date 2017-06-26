from setuptools import setup, find_packages

setup(
    name="pytest-reph",
    version='0.0.1a1',
    description='reports hooks',
    platforms=['linux', 'osx', 'win32'],
    packages=find_packages(),
    entry_points={
        'pytest11': [
            'reph = reph',
        ],
    },
    zip_safe=False,
    install_requires=['sqlalchemy', 'pytest>=2.7.0'],
    classifiers=[
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
