"""
Bridge module for the cumulus provider
"""

from netshowlib.cumulus import common
from netshowlib.linux import bridge as linux_bridge
from netshowlib.cumulus import mstpd
import re
from collections import OrderedDict


class MstpctlStpBridgeMember(object):
    """
    class responsible for managing stp info gathered from mstpctl
    """
    def __init__(self, bridgemem, cache=None):
        self.bridgemem = bridgemem
        self._cache = None
        self.orig_cache = cache
        self._initialize_state()

    def _initialize_state(self):
        """ initialize state attribute that keeps interesting
        info about a bridge port
        """
        self._state = OrderedDict([
            ('root', []),
            ('designated', []),
            ('forwarding', []),
            ('alternate', []),
            ('discarding', []),
            ('oper_edge_port', []),
            ('network_port', []),
            ('backup', []),
            ('disabled', [])])

    @property
    def state(self):
        """
        parse through mstpctl output
        :return:  state hash with interesting info about the port
        :return: None if STP is not running the port.
        """

        if self.orig_cache:
            self._cache = self.orig_cache.get('iface').get(self.bridgemem.name)
        else:
            self._cache = mstpd.cacheinfo().get('iface').get(self.bridgemem.name)
        # if STP is not enabled on the interface, return state as None
        # sub interfaces
        _allbridges = set(self.bridgemem.bridge_masters.keys())
        if self._cache:
            _allstpbridges = set(self._cache.keys())
        else:
            _allstpbridges = set([])
        # list bridges in disabled mode
        for _disabled_bridge in _allbridges.difference(_allstpbridges):
            _bridge = linux_bridge.BRIDGE_CACHE.get(_disabled_bridge)
            if not _bridge:
                _bridge = Bridge(_disabled_bridge, self.orig_cache)
                linux_bridge.BRIDGE_CACHE[_disabled_bridge] = _bridge
            self._state['disabled'].append(_bridge)

        if not self._cache:
            return self._state
        self._initialize_state()
        for _bridgename, _stpinfo in self._cache.iteritems():
            _bridge = linux_bridge.BRIDGE_CACHE.get(_bridgename)
            if not _bridge:
                _bridge = Bridge(_bridgename, self.orig_cache)
                linux_bridge.BRIDGE_CACHE[_bridgename] = _bridge
            if _stpinfo.get('role') == 'root':
                self._state['root'].append(_bridge)
            elif _stpinfo.get('role') == 'designated':
                self._state['designated'].append(_bridge)
            elif _stpinfo.get('role') == 'alternate':
                self._state['alternate'].append(_bridge)
            elif _stpinfo.get('role') == 'backup':
                self._state['backup'].append(_bridge)

            if _stpinfo.get('state') == 'forwarding':
                self._state['forwarding'].append(_bridge)
            elif _stpinfo.get('state') == 'discarding':
                self._state['discarding'].append(_bridge)

            if _stpinfo.get('oper_edge_port') == 'yes':
                self._state['oper_edge_port'].append(_bridge)
            elif _stpinfo.get('network_port') == 'yes':
                self._state['network_port'].append(_bridge)

        return self._state


class MstpctlStpBridge(object):
    """
    class responsible to managing stp info gathered from mstpctl
    """
    def __init__(self, bridge, cache=None):
        self.bridge = bridge
        self._root_priority = None
        self._bridge_priority = None
        if cache:
            self._cache = cache.get('mstpd').get('bridge')
        else:
            self._cache = mstpd.cacheinfo().get('bridge')
        self.orig_cache = cache
        self._stpdetails = self._cache.get(self.bridge.name)
        self.initialize_member_state()

    def is_root(self):
        """
        :return: True if switch is root for bridge domain
        """
        return self._stpdetails.get('designated_root') == \
            self._stpdetails.get('bridge_id')

    @property
    def root_port(self):
        """
        :return: root port
        """
        return self._stpdetails.get('root_port')

    @property
    def root_priority(self):
        """
        :return root priority
        """
        return int(self._stpdetails.get('designated_root').split('.')[0]) * 4096

    @property
    def bridge_priority(self):
        """
        :return: bridge priority
        """
        return int(self._stpdetails.get('bridge_id').split('.')[0]) * 4096

    def initialize_member_state(self):
        self._member_state = {
            'root': [],
            'designated': [],
            'alternate': [],
            'oper_edge_port': [],
            'network_port': [],
            'discarding': [],
            'forwarding': [],
            'backup': []
        }

    def append_member_state_from_roles(self, iface_to_add, stpinfo):
        if stpinfo.get('role') == 'root':
            self._member_state['root'].append(iface_to_add)
        elif stpinfo.get('role') == 'designated':
            self._member_state['designated'].append(iface_to_add)
        elif stpinfo.get('role') == 'alternate':
            self._member_state['alternate'].append(iface_to_add)
        elif stpinfo.get('role') == 'backup':
            self._member_state['backup'].append(iface_to_add)

    def append_member_state_from_state(self, iface_to_add, stpinfo):
        if stpinfo.get('state') == 'forwarding':
            self._member_state['forwarding'].append(iface_to_add)
        elif stpinfo.get('state') == 'discarding':
            self._member_state['discarding'].append(iface_to_add)

    def append_member_state_from_other_attrs(self, iface_to_add, stpinfo):
        if stpinfo.get('oper_edge_port') == 'yes':
            self._member_state['oper_edge_port'].append(iface_to_add)
        elif stpinfo.get('network_port') == 'yes':
            self._member_state['network_port'].append(iface_to_add)

    @property
    def member_state(self):
        """
        :return: stp state of iface members of the bridge
        """
        self.initialize_member_state()
        for _ifacename, _stpinfo in self._stpdetails.get('ifaces').iteritems():
            _iface_to_add = self.bridge.members.get(_ifacename)
            self.append_member_state_from_roles(_iface_to_add, _stpinfo)
            self.append_member_state_from_state(_iface_to_add, _stpinfo)
            self.append_member_state_from_other_attrs(_iface_to_add, _stpinfo)

        return self._member_state


class BridgeMember(linux_bridge.BridgeMember):
    """
    Class responsible for cumulus bridge member that is not a bond
    """

    @property
    def stp(self):
        """
        :return: ``None`` if STP is disabled
        :return: :class:`KernelStpBridge` instance if stp_state == 1
        :return: :class:`MstpctlStpBridge` instance if stp_state == 2
        """
        if self.read_from_sys('bridge/stp_state') == '2':
            self._stp = MstpctlStpBridgeMember(self, self._cache)
            return self._stp
        return super(BridgeMember, self).stp

    @property
    def native_vlan(self):
        """
        :return: native vlan for the vlan aware bridge
        """
        if self.read_from_sys('bridge/stp_state') == '2':
            return self.vlan_aware_vlan_list('untagged_vlans')

    @property
    def vlan_filtering(self):
        """
        :return: Determines if port is vlan aware or not
        """
        if self.read_from_sys('brport/vlans'):
            return True
        return False

    @property
    def vlan_list(self):
        """
        :return: list of vlans include native vlan if vlan aware
        :return: list of all tagged vlans if using classic driver
        """
        if self.vlan_filtering:
            return self.vlan_aware_vlan_list('vlans')
        else:
            return super(BridgeMember, self).vlan_list

    def vlan_aware_vlan_list(self, type_of_vlan):
        """
        :param type_of_vlan:  can be 'untagged_vlans' or 'vlans'
        :return: list of vlans supported on vlan aware physical/bond port
        TODO: move to common.py because used by bond and phy bridgemem
        """
        vlan_list = []
        attr_value = "brport/%s" % (type_of_vlan)
        bitmap_array = self.read_from_sys(attr_value)
        if bitmap_array:
            vlanid = 0
            for bit32entry in bitmap_array:
                hex32entry = re.sub('0x', '', bit32entry).strip()
                # convert hex entry to binary entry. Obtained from
                # Stackoverflow
                scale = 16
                num_of_bits = 32
                # converts hex string into binary string
                mod32bit = bin(int(hex32entry, scale))[2:].zfill(num_of_bits)
                # loop over the reverse of `range(32)` since vlans are listed
                # from left to right
                for i in reversed(range(32)):
                    # If vlan bit is set to one, add it to the vlan list
                    if mod32bit[i] == '1':
                        vlan_list.append(str(vlanid))
                    # increment vlan after from the list when check is done
                    vlanid += 1
        return vlan_list


class Bridge(linux_bridge.Bridge):
    """ Bridge class for the cumulus provider
    """
    def __init__(self, name, cache=None):
        linux_bridge.Bridge.__init__(self, name, cache)
        self._vlan_filtering = 0

    @property
    def vlan_filtering(self):
        """
        :return the vlan filtering setting. If set to 1 trunk config is placed
         under the physical port and can be seen using bridge vlan show command
        """
        self._vlan_filtering = 0
        if common.is_vlan_aware_bridge(self.name):
            self._vlan_filtering = 1
        return self._vlan_filtering

    @property
    def stp(self):
        """
        :return: ``None`` if STP is disabled
        :return: :class:`KernelStpBridge` instance if stp_state == 1
        :return: :class:`MstpctlStpBridge` instance if stp_state == 2
        """
        if self.read_from_sys('bridge/stp_state') == '2':
            self._stp = MstpctlStpBridge(self, self._cache)
            return self._stp
        return super(Bridge, self).stp

    @property
    def members(self):
        """
        Note it converts members into Cumulus Bridgemembers not Linux bridgemembers.
        :return: list of bridge port members
        """
        self._get_members(BridgeMember)
        return self._members
