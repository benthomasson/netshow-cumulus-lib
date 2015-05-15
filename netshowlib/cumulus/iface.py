"""
Iface module for Cumulus Provider
"""
from netshowlib import netshowlib as nn
from netshowlib.linux import common
from netshowlib.linux import iface as linux_iface
from netshowlib.cumulus import asic
import re
import os

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

    @classmethod
    def asic(cls):
        """ return class instance that matches switching asic used on the cumulus switch
        """
        if os.path.exists('/etc/bcm.d/config.bcm'):
            return asic.BroadcomAsic()
        return None


    def is_mgmt_initial_test(self):
        """
        :return: sets port bitmap entry ``MGMT_INT``. This applies to any ethX and lo interface.
        """
        self._port_type = common.clear_bit(self._port_type, linux_iface.MGMT_INT)
        if re.match(r'eth\d+$', self.name):
            self._port_type = common.set_bit(self._port_type, linux_iface.MGMT_INT)
        elif self.is_loopback():
            self._port_type = common.set_bit(self._port_type, linux_iface.MGMT_INT)


    def is_mgmt(self):
        """
        :return: true if port is a management port
        """
        self.is_mgmt_initial_test()
        return common.check_bit(self._port_type, linux_iface.MGMT_INT)


    def is_phy_initial_test(self):
        """
        :return: sets port bitmap entry ``PHY_INT``
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
        """ type of connector physical switch has
        Returns:
            int. The return code::
                0 -- SFP (1G/10G)
                1 -- SFP+ (10G)
                2 -- QSFP (40G or 4x10G)

        """
        if not self.is_phy():
            return ''

    def initial_speed(self):
        """
        returns initial speed of the physical port
        """
        # if not a physical port, return none
        if not self.is_phy():
            return None

        _asic = self.asic()
        if _asic:
            return _asic.portspeed(self.name)

    @property
    def speed(self):
        """
        :return: port speed in MB
        If the port is down (not admin down) unfortunately speed == 0. \
            Someone fix this pretty please?
        If port is admin down get speed from broadcom initialization files
        """
        if self.linkstate == 0:
            self._speed = self.initial_speed()
        else:
            self._speed = super(Iface, self).speed

        return self._speed
