# pylint: disable=R0902
# pylint: disable=W0232
# pylint: disable=C0325
# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101

""" Module for Managing switch neighbor printout for the cumulus provider
"""

import netshow.linux.show_neighbors as linux_showneighbors
import netshowlib.cumulus.cache as cumulus_cache
import json
from netshow.linux.netjson_encoder import NetEncoder
from netshow.cumulus import print_iface


class ShowNeighbors(linux_showneighbors.ShowNeighbors):
    """
    Class responsible for printing out basic cumulus device neighbor info
    """
    def run(self):
        """
        :return: basic neighbor information based on data obtained on netshow-lib
        """
        feature_cache = cumulus_cache.Cache()
        feature_cache.run()
        for _ifacename in feature_cache.lldp.keys():
            self.ifacelist[_ifacename] = print_iface.iface(_ifacename, feature_cache)

        if self.use_json:
            return json.dumps(self.ifacelist,
                              cls=NetEncoder, indent=4)

        return self.print_neighbor_info()
