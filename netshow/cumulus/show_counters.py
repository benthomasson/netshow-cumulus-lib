# pylint: disable=E0611
""" Module for printing show counter information
"""

import netshowlib.linux.iface as linux_iface
import netshowlib.cumulus.iface as cumulus_iface
from netshow.linux.netjson_encoder import NetEncoder
from netshow.cumulus import print_iface
import netshowlib.cumulus.cache as cumulus_cache
from collections import OrderedDict
import json
from tabulate import tabulate
from flufl.i18n import initialize


_ = initialize('netshow-cumulus-lib')


class ShowCounters(object):
    """
    Class responsible for printing out basic linux device neighbor info
    """
    def __init__(self, **kwargs):
        self.use_json = kwargs.get('--json') or kwargs.get('-j')
        self.ifacelist = OrderedDict()

    def run(self):
        """
        :return: basic neighbor information based on data obtained on netshow-lib
        """
        feature_cache = cumulus_cache.Cache()
        feature_cache.run()
        for _ifacename in linux_iface.portname_list():
            _testiface = cumulus_iface.iface(_ifacename, feature_cache)
            if isinstance(_testiface, cumulus_iface.Iface) and \
                    _testiface.is_phy():
                self.ifacelist[_ifacename] = print_iface.PrintIface(_testiface)

        if self.use_json:
            return json.dumps(self.ifacelist,
                              cls=NetEncoder, indent=4)

        return self.print_counters()

    def print_counters(self):
        """
        :return: cli output of netshow counters
        """
        _header = [_(''), _('port'), _('speed'), _('mode'), '',
                   _('ucast'), _('mcast'), _('bcast'), _('errors')]
        _table = []
        for _piface in self.ifacelist.values():
            _rx_counters = _piface.iface.counters.rx
            _tx_counters = _piface.iface.counters.tx
            _table.append([_piface.linkstate, _piface.name,
                           _piface.speed, _piface.port_category,
                           _('rx'), _rx_counters.get('unicast'),
                           _rx_counters.get('multicast'),
                           _rx_counters.get('broadcast'),
                           _rx_counters.get('errors')])
            _table.append(['', '', '', '', _('tx'),
                           _tx_counters.get('unicast'),
                           _tx_counters.get('multicast'),
                           _tx_counters.get('broadcast'),
                           _tx_counters.get('errors')])
        return tabulate(_table, _header)
