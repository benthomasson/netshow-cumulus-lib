""" Module for Managing switch system information printout
"""

from netshowlib.cumulus.system_summary import SystemSummary
from netshow.linux import show_system as linux_system
from flufl.i18n import initialize

_ = initialize('netshow-linux-lib')


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

        pd = self.system.platform_info
        # If platform detect does not work.
        # TODO make this better....
        if not pd:
            return super(ShowSystem, self).cli_output()

        chip = pd.get('chipset')
        cpu = pd.get('processor')
        _str = ''
        _str = "\n%s %s\n" % (pd.get('manufacturer'), pd.get('model'))
        _str += "%s %s %s\n" % (self.system.os_name, _('version'),
                                self.system.version)
        _str += "%s: %s\n\n" % (_('build'), self.system.os_build)
        _str += "%s: %s %s %s\n\n" % (_('chipset'),
                                      chip.get('manufacturer'),
                                      chip.get('family'),
                                      chip.get('model'))
        _str += "%s: %s\n\n" % (_('port config'), pd.get('ports'))
        _str += "%s: (%s) %s %s %s %s\n\n" % (_('cpu'),
                                              self.system.arch,
                                              cpu.get('manufacturer'),
                                              cpu.get('family'),
                                              cpu.get('model'),
                                              cpu.get('speed'))
        _str += "%s: %s\n" % (_('uptime'), self.uptime)
        return _str
