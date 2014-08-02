#!/usr/bin/python

"""
Usage:
    example.py show ip route [<ip>|<ip/mask>] 
    example.py show ip interface [<interface>] 

Help:
    -h --help     Show this screen

"""

import sys
from network_docopt import NetworkDocopt
from subprocess import check_output

class ExampleCLI(NetworkDocopt):

    def __init__(self, docstring):
        NetworkDocopt.__init__(self, docstring)

    def run(self):
        args = self.args

        if self.closest_matches:
            print '\n'.join(self.closest_matches)
            return

        if args['show']:
            if args['ip']:
                if args['route']:
                    if args['<ip>']:
                        print check_output(['ip', 'route', 'get', args['<ip>']])
                    elif args['<ip/mask>']:
                        print check_output(['ip', 'route', 'get', args['<ip/mask>']])
                    else:
                        print check_output(['ip', 'route', 'show'])

if __name__ == "__main__":
    print_options = False

    if sys.argv[-1] == 'options':
        print_options = True
        sys.argv = sys.argv[0:-1]

    cli = ExampleCLI(__doc__)

    # If the last arg was 'options' then we need to print the possible options
    # for the command entered.  This is used to feed the bash autocomplete
    # script at /usr/share/bash-completion/completions/example.py
    if print_options:
        cli.print_options()
    else:
        cli.run()
