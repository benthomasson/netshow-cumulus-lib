# pylint: disable=R0902

"""
Module for printout of 'netshow interfaces' of the Cumulus provider
"""

from collections import OrderedDict
from tabulate import tabulate
import netshowlib.cumulus.cache as cumulus_cache
from netshowlib.cumulus import iface as cumulus_iface
from netshow.cumulus.print_iface import PrintIface
from netshow.linux import print_iface as linux_printiface
from flufl.i18n import initialize

_ = initialize('netshow-cumulus-lib')


class ShowInterfaces(linux_printiface.PrintIface):
    """ Class responsible for the 'netshow interfaces' printout for \
        the cumulus provider
    """
    def __init__(self, **kwargs):
        linux_printiface.PrintIface.__init__(self, **kwargs)
