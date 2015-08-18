"""
module for mstpd functions
"""
from netshowlib.linux import common as linux_common
import io
import re


def cacheinfo():
    _mstpdcache = MstpdInfo()
    return _mstpdcache.run()


class MstpdInfo(object):

    def __init__(self):
        self.is_bridge_info = None
        self.newbridgename = None
        self.bridgename = None
        self.iface = None
        self.bridge_loc = None
        self.textio = None
        self.bridgehash = {'bridge': {}, 'iface': {}}

    @property
    def mstpctl_output(self):
        """
        :returns: mstpctl showall output(raw)
        """

        result = ''
        try:
            result = linux_common.exec_command('/sbin/mstpctl showall')
        except (ValueError, IOError):
            pass
        return result

    def set_bridge_name(self, line):
        """
        when parsing mstpctl, set the bridge name. and reset iface and bridge_loc variables.
        """
        if self.newbridgename and self.bridgename != self.newbridgename:
            self.bridgename = self.newbridgename
            self.newbridgename = None

        if line.startswith('BRIDGE'):
            splitline = line.split()
            self.newbridgename = splitline[1].split(',')[0]
            self.iface = None
            self.bridge_loc = None
            return True
        return False

    def run(self):
        """
        execute mstpctl and parse it. return hash of most of the mstpctl output.
        mstpctl needs to have JSON output. would do away with this class.
        """
        self.textio = io.StringIO(self.mstpctl_output)
        for line in self.textio:
            if len(line.strip()) <= 0:
                continue
            if len(line.split(',')) > 2:
                continue
            if self.set_bridge_name(line):
                continue

            if self.bridgename:
                self.set_next_col_at()
                if self.initialize_bridgehash(line):
                    continue
                elif self.initialize_ifacehash(line):
                    continue

                self.create_iface_bridge_hash_to_write_to()
                self.update_stp_attributes(line)

        return self.bridgehash

    def set_next_col_at(self):
        """
        :return: column width to use. if parsing bridge entry, use 26 if parsing iface entry use 45.
        """
        if self.is_bridge_info:
            self.next_col_at = 26
        else:
            self.next_col_at = 45

    def initialize_bridgehash(self, line):
        """
        initialize bridge and bridge->ifaces section of the bridgehash attribute.
        """
        if line.split()[0] == self.bridgename:
            self.bridgehash['bridge'][self.bridgename] = {}
            self.bridgehash['bridge'][self.bridgename]['ifaces'] = {}
            self.is_bridge_info = True
            self.bridge_loc = None
            self.iface = None
            return True
        return False

    def initialize_ifacehash(self, line):
        """
        initialize the iface portion of the bridgehash attribute.
        """
        if len(line.split()[0].split(':')) == 2:
            self.iface = line.split()[0].split(':')[1]
            self.is_bridge_info = False
            self.bridge_loc = None
            return True
        return False

    def create_iface_bridge_hash_to_write_to(self):
        """
        determine whether to print iface info  or bridge info and use the right class/hash for the job.
        """
        if not self.bridge_loc:
            if self.iface:
                self.bridgehash['bridge'][self.bridgename]['ifaces'][self.iface] = {}
                self.bridge_loc = self.bridgehash['bridge'][self.bridgename]['ifaces'][self.iface]
                if not self.bridgehash.get('iface').get(self.iface):
                    self.bridgehash['iface'][self.iface] = {}
                master_iface = self.iface.split('.')[0]
                self.bridgehash['iface'][master_iface][self.bridgename] = self.bridge_loc
            else:
                self.bridge_loc = self.bridgehash['bridge'].get(self.bridgename)

    def update_stp_attributes(self, line):
        """
        decided to stick to scraping mstpctl. so need to do a little magic on the text output
        """
        # col splitting magic. courteous of Jtoppins@cumulus
        if len(line) > 45:
            col = line[:self.next_col_at].strip().split()
            subkey = '_'.join(col[0:-1]).lower()
            value = col[-1]
            self.bridge_loc[subkey] = value.lower()
            col = line[self.next_col_at:].strip().split()
            subkey = '_'.join(col[0:-1]).lower()
            value = col[-1]
            self.bridge_loc[subkey] = value.lower()
        else:
            line = re.sub(r'\(.*\)', '', line)
            col = line.strip().split()
            subkey = '_'.join(col[0:-1]).lower()
            value = col[-1]
            self.bridge_loc[subkey] = value.lower()
