from flufl.i18n import SimpleStrategy
from flufl.i18n import registry


def i18n_app():
    """
    blah
    """
    strategy = SimpleStrategy('netshow-cumulus-lib')
    return registry.register(strategy)

_ = i18n_app()._
