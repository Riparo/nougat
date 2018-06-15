import pytest
import argparse


class TestManage:

    def test_bind_command(self, app):

        def test():

            return 'hello world'

        app.manager.command(test)

        assert app.manager.up('test') == 'hello world'

    def test_bind_with_name(self, app):

        def with_name():

            return 'hello'

        app.manager.command(with_name, name='hello')

        assert app.manager.up('hello') == 'hello'

    def test_boolean_arg(self, app):

        def boolean(verbose=True):
            if verbose:
                return 'verbose'
            return 'emm'

        app.manager.command(boolean)

        assert app.manager.up('boolean') == 'verbose'
        assert app.manager.up('boolean', '--no-verbose') == 'emm'

    def test_boolean_arg_with_false_default_value(self, app):

        def boolean(verbose=False):
            if verbose:
                return 'verbose'
            return 'emm'

        app.manager.command(boolean)

        assert app.manager.up('boolean') == 'emm'
        assert app.manager.up('boolean', '--verbose') == 'verbose'

    def test_add_sub_arg(self, app):

        def hello(name):
            return 'hello {}'.format(name)

        app.manager.command(hello)

        assert app.manager.up('hello', 'world') == 'hello world'

    def test_extension_add_command(self, app):

        class Extension:

            def __init__(self, app=None):

                if app:
                    self.set_up(app)

            def set_up(self, app):

                app.manager.command(self.command, name="extension")

            def command(self):
                return 'hello'

        e = Extension(app)

        assert app.manager.up('extension') == 'hello'
