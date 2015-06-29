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


class ShowNeighbors(linux_showneighbors.ShowNeighbors):
    """
    Class responsible for printing out basic cumulus device neighbor info
    """
    def __init__(self, cl):
        linux_showneighbors.ShowNeighbors.__init__(self, cl)
        self.cache = cumulus_cache
