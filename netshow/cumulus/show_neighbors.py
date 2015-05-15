# pylint: disable=E0611
""" Module for Managing switch neighbor printout for the cumulus provider
"""

import netshow.linux.show_neighbors as linux_showneighbors

class ShowNeighbors(linux_showneighbors.ShowNeighbors):
    """
    Class responsible for printing out basic switch neighbor info for the Cumulus provider
    """
    def __init__(self, **kwargs):
        pass

    def run(self):
        """
        :return: basic neighbor information based on data obtained on netshow-lib
        """
        pass
