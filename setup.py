# pylint: disable=c0111
try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup
setup(
    name='network-docopt',
    version='0.1.0',
    description="Network Docopt",
    url="https://github.com/dwalton76/NetworkDocopt",
    author='Daniel Walton',
    author_email='dwalton@cumulusnetworks.com',
    py_modules=['network_docopt'],
    install_requires=[
        'ipaddr'
    ],
    scripts=['bin/network-docopt-example'],
    data_files=[('usr/share/bash-completion/completions',
                 ['completions/network-docopt-example'])]
)
