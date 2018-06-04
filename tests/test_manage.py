import pytest
from nougat.manage import Manager
import argparse


class TestManage:

    def test_bind_command(self, app):

        manager = Manager(app)

        def test():

            return 'hello world'

        manager.command(test)

        assert manager.up('test') == 'hello world'

    def test_bind_with_name(self, app):
        manager = Manager(app)

        def with_name():

            return 'hello'

        manager.command(with_name, name='hello')

        assert manager.up('hello') == 'hello'

    def test_boolean_arg(self, app):
        manager = Manager(app)

        def boolean(verbose=True):
            if verbose:
                return 'verbose'
            return 'emm'

        manager.command(boolean)

        assert manager.up('boolean') == 'verbose'
        assert manager.up('boolean', '--no-verbose') == 'emm'

    def test_boolean_arg_with_false_default_value(self, app):
        manager = Manager(app)

        def boolean(verbose=False):
            if verbose:
                return 'verbose'
            return 'emm'

        manager.command(boolean)

        assert manager.up('boolean') == 'emm'
        assert manager.up('boolean', '--verbose') == 'verbose'

    def test_add_sub_arg(self, app):

        manager = Manager(app)

        def hello(name):
            return 'hello {}'.format(name)

        manager.command(hello)

        assert manager.up('hello', 'world') == 'hello world'
