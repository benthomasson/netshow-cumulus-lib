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
    pass
