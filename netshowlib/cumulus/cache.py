# pylint: disable-msg=E0611
"""
This module produces the cache info for Linux
"""

from netshowlib.linux.cache import Cache as linuxCache


class Cache(linuxCache):
    """
    This class produces the cache info for Cumulus \
        networking such as ip addressing, lldp, QOS
    """
    def __init__(self):
        linuxCache.__init__(self)
        self.feature_list['counters'] = 'cumulus'
        self.feature_list['mstpd'] = 'cumulus'
        self.feature_list['asic'] = 'cumulus'
