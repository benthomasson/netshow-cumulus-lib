"""
Module for running asic specific tasks
"""

from netshowlib.linux import common
import re


class BroadcomAsic(object):
    """
    class with functions to get names and initial port speed from broadcom
    """
    def __init__(self):
        self.name = 'broadcom'


    @classmethod
    def portname(cls, linuxname):
        """
        Returns:
            broadcom name of the physical port
        """
        _porttab = '/var/lib/cumulus/porttab'
        porttab = common.read_file(_porttab)
        if porttab is None:
            return None

        for line in porttab:
            _match_regex = re.compile(r'^%s\s+(\w+)' % (linuxname))
            _m0 = re.match(_match_regex, line)
            if _m0:
                return _m0.group(1)

        return None

    def connector_type(self, linuxname):
        """ type of connector physical switch has
        Args:
            linuxname: linux kernel name of the physical interface
        Returns:
            int. The return code::
                1 -- RJ-45 (1G/10G)
                2 -- SFP+ (10G)
                3 -- QSFP (40G or 4x10G)
        """
        _portname = self.portname(linuxname)
        _speed = self.portspeed(linuxname)
        if _portname.startswith('ge'):
            return 1
        elif _speed == '10000':
            return 2
        elif _speed == '40000':
            return 3

    def portspeed(self, linuxname):
        """
        :param linuxname: port name of the physical port according to \
            linux kernel. Example: swp1
        :return: initial speed of the port. Would like one day to return actual speed
        regardless of whether port is up or down. so gets speed from asic not from kernel
        """
        _bcmfile = '/etc/bcm.d/config.bcm'
        bcm_config_file = common.read_file(_bcmfile)

        # if bcm config file doesn't exist, return none
        if bcm_config_file is None:
            return None

        for line in bcm_config_file:
            _match_str = r"^port_init_speed_%s=(\d+)" % (self.portname(linuxname))
            _match_regex = re.compile(_match_str)
            _m0 = re.match(_match_regex, line)
            if _m0:
                return _m0.group(1)
        return None
