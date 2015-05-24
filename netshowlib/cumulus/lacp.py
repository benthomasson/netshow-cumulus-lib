"""
This module contains the Lacp Class responsible for methods
and attributes regarding Lacp support on Bond interfaces
"""

import netshowlib.linux.lacp as linux_lacp
import netshowlib.linux.common as linux_common

class Lacp(linux_lacp.Lacp):
    """ Lacp class attributes

    * **sys_priority**: LACP system priority. Used in conjunction with the \
        system mac of a bond to create a system Ia
    * **rate**: LACP rate/timeout.
    * **partner_mac**: LACP partner mac. Collected but not used. May be useful \
        in the future

    """
    def __init__(self, name):
        linux_lacp.Lacp.__init__(self, name)
        self._lacp_bypass = None

    @property
    def lacp_bypass(self):
        """
        :return: '1', '0' if LACP bypass is supported. '1' means that its active
        :return: None if not supported on this Cumulus Linux release
        """
        return linux_common.read_from_sys('bonding/lacp_bypass_allowed', self.name)
