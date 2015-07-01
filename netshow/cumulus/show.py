# print() is required for py3 not py2. so need to disable C0325
# pylint: disable=C0325
# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101
"""
Usage:
    netshow neighbors [--json | -j ]
    netshow counters [errors] [all] [--json | -j ]
    netshow system [--json | -j ]
    netshow interface [ access | bridges | bonds | bondmems | mgmt | l2 | l3 | phy | trunks | <iface> ] [all] [--mac | -m ] [--oneline | -1  | --json | -j]
    netshow (--version | -v)

Help:
    * default is to show intefaces only in the UP state.
    interface                 summary info of all interfaces
    interface access          summary of physical ports with l2 or l3 config
    interface bonds           summary of bonds
    interface bondmems        summary of bond members
    interface mgmt            summary of mgmt ports
    interface l3              summary of ports with an IP.
    interface l2              summary of access, trunk and bridge interfaces
    interface phy             summary of physical ports
    interface trunks          summary of trunk interfaces
    interface <interface>     list summary of a single interface
    system                    system information
    neighbors                 physical device neighbor information

Options:
    all        show all ports in_ndude those are down or admin down
    --mac      show inteface MAC in output
    --version  netshow software version
    --oneline  output each entry on one line
    -1         alias for --oneline
    --json     print output in json
"""
import sys
from network_docopt import NetworkDocopt
from netshowlib._version import get_version
from netshow.cumulus.show_counters import ShowCounters
from netshow.cumulus.show_system import ShowSystem
from netshow.cumulus.show_interfaces import ShowInterfaces
from netshow.cumulus.show_neighbors import ShowNeighbors



def run():
    """ run cumulus netshow version """
    if sys.argv[-1] == 'options':
        print_options = True
        sys.argv = sys.argv[0:-1]
    else:
        print_options = False

    _nd = NetworkDocopt(__doc__)
    if print_options:
        _nd.print_options()
    else:
        if _nd.get('interface'):
            _showint = ShowInterfaces(_nd)
            print(_showint.run())
        elif _nd.get('system'):
            _showsys = ShowSystem(_nd)
            print(_showsys.run())
        elif _nd.get('neighbors'):
            _shownei = ShowNeighbors(_nd)
            print(_shownei.run())
        elif _nd.get('counters'):
            _showcounters = ShowCounters(_nd)
            print(_showcounters.run())
        elif _nd.get('--version') or _nd.get('-v'):
            print(get_version())
        else:
            print(__doc__)
