import argparse
import inspect
import re
import sys

PARAM_RE = re.compile(r'^\s+:param (\w+): (.+)$', re.M)


class Manager(object):
    """
    example.py

    ```python
    from nougat import Nougat

    app = Nougat()


    async def middleware(response):

        response.content = 'Hello world'

    app.use(middleware)

    app.manager.up()
    ```

    then just run `python example.py run`, the server is starting.

    """

    def __init__(self, app):

        self.app = app
        self.parser = argparse.ArgumentParser(description="Manage %s" % self.app.app.capitalize())
        self.parsers = self.parser.add_subparsers(dest='sub_command')
        self.handlers = {}

        self.command(self.app.run)

    def command(self, func, name=None):
        if not name:
            name = func.__name__

        header = '\n'.join([s.strip() for s in (func.__doc__ or '').split('\n')
                            if not s.strip().startswith(':') and len(s.strip()) > 0])

        parser = self.parsers.add_parser(name, description=header)

        sig = inspect.signature(func)

        args_docs = dict(PARAM_RE.findall(func.__doc__ or ""))

        for param in sig.parameters.values():

            if param.name in ['module', 'app']:
                continue

            arg_name = param.name.replace('_', '-').lower()
            arg_help = args_docs.get(param.name, '')

            if param.default is param.empty:
                parser.add_argument(arg_name, help=arg_help)
                continue

            if isinstance(param.default, bool):
                if param.default is True:
                    parser.add_argument("--no-{}".format(arg_name), dest=param.name, action="store_false",
                                        help="Disable {}".format((arg_help or param.name).lower()))
                else:
                    parser.add_argument("--{}".format(arg_name), dest=param.name, action="store_true",
                                        help="Enable {}".format((arg_help or param.name).lower()))

                continue

            parser.add_argument("--" + arg_name,
                                type=param.annotation if param.annotation is not param.empty else type(param.default),
                                default=param.default, help="{} {}".format(arg_help, param.default))

        self.handlers[name] = func

    def up(self, *args):
        if not args:
            args = sys.argv[1:]

        args = self.parser.parse_args(args)

        handler = self.handlers.get(args.sub_command, None)

        if not handler:
            self.parser.print_help()
        else:

            _args = vars(args)
            _args.pop('sub_command')

            inner_param = {
                'app': self.app
            }
            parameters = inspect.signature(handler).parameters.keys()

            for k, v in inner_param.items():
                if k in parameters:
                    _args[k] = v

            return handler(**_args)
