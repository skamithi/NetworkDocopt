# Overview
NetworkDocopt is a command line argument parser for networking focused applications.  This was heavily inspired by the docopt module at http://docopt.org/ (no code from docopt was used however). The key differences are:

- Support for specific types of <> variable tags with sanity checking:
    - \<ip\> or \<source-ip\>   : Must enter a valid IPv4 Address
    - \<ip/mask\>             : Must enter a valid IPv4 subnet
    - \<interface\>           : Must enter a valid "lo, eth0, swp5, etc" interfacae
    - \<name> or \<cleartext\> : Any text will do
    - \<number\>              : Must enter a number

- Support for partial command line options.  If your program foo has a "foo show summary" option you can also enter "foo sh sum"

- Support for integration into bash's auto-complete mechanism


# Example
- See network-docopt-example for an example of how to use this module
- For bash \<tab\> auto-completion and bash \<tab\>\<tab\> "show me available options" you must create a small bash script in /usr/share/bash-completion/completions/ like so:
- cp completions/network-docopt-example /usr/share/bash-completion/completions/

This bash script will call network-docopt-example with 'options' as the last argument. For instance if you type "network-docopt-example show ip <tab><tab>" the bash script will call "network-docopt-example show ip options" which will return "route" and "interface". This tells bash what the next options are.

# Installation
# Installing via python
Run ``python setup.py install ``

## Installing via a deb
We have not hosted a .deb for this project yet but you can build a .deb via:
 python setup.py --command-packages=stdeb.command sdist_dsc bdist_deb

This will place a .deb in the deb_dist directory, just "dpkg -i" to install it.
Example:

```
root@cel-redxp-99:~/NetworkDocopt/deb_dist# ls -l *.deb
-rw-r--r-- 1 root root 5650 May 20 13:57 python-network-docopt_1.0-1_all.deb
root@cel-redxp-99:~/NetworkDocopt/deb_dist#
root@cel-redxp-99:~/NetworkDocopt/deb_dist#
root@cel-redxp-99:~/NetworkDocopt/deb_dist# dpkg -i python-network-docopt_1.0-1_all.deb
(Reading database ... 28658 files and directories currently installed.)
Preparing to replace python-network-docopt 0.1.0-cl3.0 (using python-network-docopt_1.0-1_all.deb) ...
Unpacking replacement python-network-docopt ...
Setting up python-network-docopt (1.0-1) ...
root@cel-redxp-99:~/NetworkDocopt/deb_dist#
```
