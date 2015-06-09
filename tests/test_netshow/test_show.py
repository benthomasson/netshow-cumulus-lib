# http://pylint-messages.wikidot.com/all-codes
# pylint: disable=R0913
# disable unused argument
# pylint: disable=W0613
# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# disable invalid name
# pylint: disable=C0103
# pylint: disable=F0401
# pylint: disable=E0611
# pylint: disable=W0611

from asserts import assert_equals
import netshow.cumulus.show as show
import mock


def test_interface_related():
    for _val in ['trunks', 'access', 'l3', 'trunks', 'phy',
                 'l2', 'bridges', 'bonds', 'bondmems',
                 'interface']:

        results = {_val: True}
        assert_equals(show._interface_related(results), True)


@mock.patch('netshow.cumulus.show.docopt')
@mock.patch('netshow.cumulus.show.ShowInterfaces')
def test_run_show_interfaces(mock_showint, mock_docopt):
    # netshow interfaces
    mock_docopt.return_value = {'trunks': True}
    show.run()
    assert_equals(mock_showint.call_count, 1)


@mock.patch('netshow.cumulus.show.docopt')
@mock.patch('netshow.cumulus.show.ShowSystem')
def test_run_show_system(mock_showsys, mock_docopt):
    # netshow system
    mock_docopt.return_value = {'system': True}
    show.run()
    assert_equals(mock_showsys.call_count, 1)


@mock.patch('netshow.cumulus.show.docopt')
@mock.patch('netshow.cumulus.show.ShowNeighbors')
def test_run_show_neighbors(mock_shownei, mock_docopt):
    # netshow system
    mock_docopt.return_value = {'neighbors': True}
    show.run()
    assert_equals(mock_shownei.call_count, 1)


@mock.patch('netshow.cumulus.show.docopt')
@mock.patch('netshow.cumulus.show.ShowCounters')
def test_run_show_counters(mock_showcounters, mock_docopt):
    # netshow system
    mock_docopt.return_value = {'counters': True}
    show.run()
    assert_equals(mock_showcounters.call_count, 1)
