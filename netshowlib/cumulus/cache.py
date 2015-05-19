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
        linuxCache.Cache.__init__(self)
        self._feature_list.append('counters')
        self.counters = {}
        self.provider = 'cumulus'
