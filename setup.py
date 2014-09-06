try:
    import DistUtilsExtra.auto
except ImportError:
    import sys
    print >> sys.stderr, \
        'To build network docopt you need apt-get install python-distutils-extra'
    sys.exit(1)

DistUtilsExtra.auto.setup(
    name='network-docopt',
    version='1.0',
    description="Network Docopt",
    url="https://github.com/dwalton76/NetworkDocopt",
    author='Daniel Walton',
    author_email='dwalton@cumulusnetworks.com',
    scripts=['bin/network-docopt-example'],
    provides=('network_docopt'),
    data_files=[('/usr/share/bash-completion/completions',
                 ['completions/network-docopt-example'])]
)
