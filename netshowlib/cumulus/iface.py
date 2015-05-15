"""
Iface module for Cumulus Provider
"""

from netshowlib import netshowlib as nn
from netshowlib.linux import common
from netshowlib.linux import iface as linux_iface
import re

def iface(name, cache=None):
    """
    calls on checks to determine best interface type match for the named interface

    :return: regular :class:`cumulus.iface <netshowlib.cumulus.iface.Iface>` or \
    :class:`cumulus bond or bond member<netshowlib.cumulus.bond.Bond>`  or  \
    :class:`cumulus bridge or bridge member <netshowlib.cumulus.bridge.Bridge>` \
    interface
    """
    # create test iface.
    test_iface = Iface(name, cache=cache)
    if test_iface.is_bridge():
        bridge = nn.import_module('netshowlib.cumulus.bridge')
        return bridge.Bridge(name, cache=cache)
    elif test_iface.is_bridgemem():
        bridge = nn.import_module('netshowlib.cumulus.bridge')
        return bridge.BridgeMember(name, cache=cache)
    elif test_iface.is_bond():
        bond = nn.import_module('netshowlib.cumulus.bond')
        return bond.Bond(name, cache=cache)
    elif test_iface.is_bondmem():
        bondmem = nn.import_module('netshowlib.cumulus.bond')
        return bondmem.BondMember(name, cache=cache)

    return test_iface


class Iface(linux_iface.Iface):
    """ Cumulus Iface Class
    """

    def is_phy_initial_test(self):
        """
        :return: sets port bitmap entry ``MGMT_INT``
        """
        self._port_type = common.clear_bit(self._port_type, linux_iface.PHY_INT)
        if re.match(r'swp\d+(s\d+)?$', self.name):
            self._port_type = common.set_bit(self._port_type, linux_iface.PHY_INT)

    def is_phy(self):
        """
        :return: true if port is a physical port
        """
        self.is_phy_initial_test()
        return common.check_bit(self._port_type, linux_iface.PHY_INT)

    @property
    def connector_type(self):
        """
        :return: connector type of the physical port
        """
        if not self.is_phy():
            return ''

    def bcm_name(self):
        """
        :return: broadcom name of the physical port
        """
        _porttab = '/var/lib/cumulus/porttab'
        porttab = common.read_file(_porttab)
        if porttab is None:
            return

        for line in porttab:
            _match_regex = re.compile('^' + self.name + '\s+(\w+)')
            _m0 = re.match(_match_regex, line)
            if _m0:
                return _m0.group(1)

    @property
    def initial_speed(self):
        """
        :return initial speed as reported by the broadcom initialization files
        """
        _bcmfile = '/etc/bcm.d/config.bcm'
        bcm_config_file = common.read_file(_bcmfile)
        if bcm_config_file is None:
            return

        for line in bcm_config_file:
            _match_str = r"^_port_init_speed_%s=(\d+)" % (self.get_bcm_name())
            _match_regex = re.compile(_match_str)
            _m0 = re.match(_match_regex, line)
            if _m0:
                return _m0.group(1)

    @property
    def speed(self):
        """
        :return: port speed in MB.
        If the port is down (not admin down) unfortunately speed == 0. \
            Someone fix this pretty please?
        If port is admin down get speed from broadcom initialization files
        """
        if self.linkstate == 0:
            self._speed = self.initial_speed
        else:
            self._speed = super(Iface, self).speed

        return self._speed
