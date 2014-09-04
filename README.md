NetworkDocopt is a command line argument parser for networking focused applications.  This was heavily inspired by the docopt module at http://docopt.org/ (no code from docopt was used however). The key differences are:

- Support for specific types of <> variable tags with sanity checking:
    - \<ip\> or \<source-ip\>   : Must enter a valid IPv4 Address
    - \<ip/mask\>             : Must enter a valid IPv4 subnet
    - \<interface\>           : Must enter a valid "lo, eth0, swp5, etc" interfacae
    - \<name> or \<cleartext\> : Any text will do
    - \<number\>              : Must enter a number

- Support for partial command line options.  If your program foo has a "foo show summary" option you can also enter "foo sh sum"

- Support for integration into bash's auto-complete mechanism

- To install run `python setup.py`

Example
- See network-docopt-example for an example of how to use this module
- For bash \<tab\> auto-completion and bash \<tab\>\<tab\> "show me available options" you must create a small bash script in /usr/share/bash-completion/completions/ like so:
- cp completions/network-docopt-example /usr/share/bash-completion/completions/

This bash script will call network-docopt-example with 'options' as the last argument. For instance if you type "network-docopt-example show ip <tab><tab>" the bash script will call "network-docopt-example show ip options" which will return "route" and "interface". This tells bash what the next options are.


