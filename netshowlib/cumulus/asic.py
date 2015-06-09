"""
Module for running asic specific tasks
"""

from netshowlib.linux import common as linux_common
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import re


PORTTAB_FILELOCATION = '/var/lib/cumulus/porttab'
BCMD_FILELOCATION = '/etc/bcm.d/config.bcm'


def switching_asic_discovery():
    """ return class instance that matches switching asic
    used on the cumulus switch
    """
    try:
        lspci_output = linux_common.exec_command('lspci -nn')
    except linux_common.ExecCommandException:
        return None

    for _line in lspci_output.decode('utf-8').split('\n'):
        _line = _line.lower()
        if re.search(r'(ethernet|network)\s+controller.*broadcom',
                     _line):
            return BroadcomAsic()


def cacheinfo():
    """
    :returns: ccache info for asic info format looks like this
    { 'kernelports':
          'swp1': { 'asicname':'xe11',
                    'initial_speed': '10000'}
      'asicports': {
          'xe11': 'swp11' }
    }
    """
    cache = {}
    asic = switching_asic_discovery()
    if asic:
        cache = asic.parse_speed_and_name_info()
    return cache


class Asic(object):
    """
    generic asic class for getting asic info
    """
    def __init__(self, name, cache=None):
        self._cache = cache
        self.ifacename = name

    def run(self):
        if not self._cache:
            cache = cacheinfo()
            return cache['kernelports'].get(self.ifacename)
        else:
            return self._cache.asic['kernelports'].get(self.ifacename)


class BroadcomAsic(object):
    """
    class with functions to get names and initial port speed from broadcom
    """
    def __init__(self):
        self.porttab = PORTTAB_FILELOCATION
        self.bcmd = BCMD_FILELOCATION
        self.asichash = {'name': 'broadcom',
                         'kernelports': {},
                         'asicports': {}}

    def parse_speed_and_name_info(self):
        self.parse_ports_file()
        self.parse_initial_speed_file()
        return self.asichash

    def parse_ports_file(self):
        """
        parses porttabs file to generate mapping between kernel
        port name and asic port name
        """
        porttab = open(self.porttab).read()
        textio = StringIO(porttab)
        for line in textio:
            if line.startswith('swp'):
                linesplit = line.split()
                self.asichash['kernelports'][linesplit[0]] = {}
                porthash = self.asichash['kernelports'][linesplit[0]]
                porthash['asicname'] = linesplit[1]
                self.asichash['asicports'][linesplit[1]] = linesplit[0]

    def parse_initial_speed_file(self):
        """
        parses initial speed info from broadcom initialization files
        """
        bcmdfile = open(self.bcmd).read()
        textio = StringIO(bcmdfile)
        for line in textio:
            if line.startswith('port_init_speed'):
                (portnamepart, speed) = line.split('=')
                asicportname = portnamepart.split('_')[-1]
                kernelportname = self.asichash['asicports'].get(asicportname)
                if kernelportname:
                    self.asichash['kernelports'][kernelportname]['initial_speed'] = speed.strip()
