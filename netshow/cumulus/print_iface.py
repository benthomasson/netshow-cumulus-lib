"""
Cumulus Iface module with print functions
"""

from netshow.linux import print_iface as linux_printiface
from flufl.i18n import initialize

_ = initialize('netshow-cumulus-lib')


class PrintIface(linux_printiface.PrintIface):
    """
    Linux Iface class with print functions
    """
    def __init__(self, name, cache=None):
        linux_printiface.PrintIface.__init__(self, name, cache)

    def speed(self):
        return _("myspeed")
