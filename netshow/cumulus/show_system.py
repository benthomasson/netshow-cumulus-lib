# pylint: disable=R0902
# pylint: disable=W0232
# pylint: disable=C0325
# pylint: disable=W0232
# pylint: disable=E0611
# pylint: disable=E1101
""" Module for Managing switch system information printout
"""

from netshowlib.cumulus.system_summary import SystemSummary
from netshow.linux import show_system as linux_system
from netshow.cumulus.common import _


class ShowSystem(linux_system.ShowSystem):
    """
    Class responsible for printing out basic switch summary info
    for the cumulus provider
    """
    def __init__(self, **kwargs):
        self.use_json = kwargs.get('--json') or kwargs.get('-j')
        self.system = SystemSummary()

    def cli_output(self):
        """
        :return: print out system info on a cumulus switch
        """

        _pd = self.system.platform_info
        # If platform detect does not work.
        # TODO make this better....
        if not _pd:
            return linux_system.ShowSystem.cli_output(self)

        chip = _pd.get('chipset')
        cpu = _pd.get('processor')
        _str = ''
        _str = "\n%s %s\n" % (_pd.get('manufacturer'), _pd.get('model'))
        _str += "%s %s %s\n" % (self.system.os_name, _('version'),
                                self.system.version)
        _str += "%s: %s\n\n" % (_('build'), self.system.os_build)
        _str += "%s: %s %s %s\n\n" % (_('chipset'),
                                      chip.get('manufacturer'),
                                      chip.get('family'),
                                      chip.get('model'))
        _str += "%s: %s\n\n" % (_('port config'), _pd.get('ports'))
        _str += "%s: (%s) %s %s %s %s\n\n" % (_('cpu'),
                                              self.system.arch,
                                              cpu.get('manufacturer'),
                                              cpu.get('family'),
                                              cpu.get('model'),
                                              cpu.get('speed'))
        _str += "%s: %s\n" % (_('uptime'), self.uptime)
        return _str
