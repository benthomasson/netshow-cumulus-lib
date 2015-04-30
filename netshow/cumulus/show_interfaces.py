# pylint: disable=R0902
# pylint: disable=W0232
"""
Module for printout of 'netshow interfaces' of the Cumulus provider
"""

from netshow.linux import print_iface as linux_printiface
from flufl.i18n import initialize

_ = initialize('netshow-cumulus-lib')


class ShowInterfaces(linux_printiface.PrintIface):
    """ Class responsible for the 'netshow interfaces' printout for \
        the cumulus provider
    """
    pass
