# pylint: disable=c0111
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup
import sys

def install_requires():
    _install_requires=''
    if sys.version_info <=(3, 0):
        _install_requires = ['ipaddr']
    return _install_requires


setup(
    name='network-docopt',
    version='0.1.1',
    description="Network Docopt",
    url="https://github.com/dwalton76/NetworkDocopt",
    author='Daniel Walton',
    author_email='dwalton@cumulusnetworks.com',
    py_modules=['network_docopt'],
    install_requires=install_requires(),
    scripts=['bin/network-docopt-example'],
    data_files=[('usr/share/bash-completion/completions',
                 ['completions/network-docopt-example'])]
)
