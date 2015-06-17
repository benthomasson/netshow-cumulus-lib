# disable docstring checking
# pylint: disable=C0111
# disable checking no-self-use
# pylint: disable=R0201
# pylint: disable=W0212
# pylint: disable=W0201
# pylint: disable=F0401
from netshowlib.cumulus import cache as cumulus_cache
import mock
from asserts import assert_equals, mock_open_str, mod_args_generator
from nose.tools import set_trace


class TestCumulusCache(object):

    def setup(self):
        self.cache = cumulus_cache.Cache()

    def test_new_attrs(self):
        assert_equals(self.cache.feature_list.get('counters'), 'cumulus')
        assert_equals(self.cache.feature_list.get('mstpd'), 'cumulus')
        assert_equals(self.cache.feature_list.get('asic'), 'cumulus')
