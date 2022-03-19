"""Module containing the logic for the gtunrealdevice entry-points."""
import re
import sys
import argparse

from gtunrealdevice.application import Application
from gtunrealdevice.config import version
from gtunrealdevice.core import DEVICES_DATA
from gtunrealdevice.utils import Printer

from gtunrealdevice.serialization import SerializedFile

from gtunrealdevice.operation import do_device_connect
from gtunrealdevice.operation import do_device_disconnect
from gtunrealdevice.operation import do_device_execute
from gtunrealdevice.operation import do_device_configure


def run_gui_application(options):
    """Run gtunrealdevice application.

    Parameters
    ----------
    options (argparse.Namespace): argparse.Namespace instance.

    Returns
    -------
    None: will invoke ``gtunrealdevice.Application().run()`` and ``sys.exit(0)``
    if end user requests `--gui`
    """
    if options.command == 'app' or options.command == 'gui':
        app = Application()
        app.run()
        sys.exit(0)


def show_dependency(options):
    if options.command == 'dependency':
        from platform import uname, python_version
        from gtunrealdevice.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        Printer.print(lst)
        sys.exit(0)


def show_version(options):
    if options.command == 'version':
        print('{} v{}'.format(Cli.prog, version))
        sys.exit(0)


def show_device_info(options):
    if options.command == 'view':
        kwargs = dict()
        pattern = r'(?i) *(?P<key>testcases?|cmdlines|device)::(?P<value>.*)?'
        for item in options.operands:
            match = re.match(pattern, item)
            if match:
                key = match.group('key')
                if key == 'testcases' or key == 'cmdlines':
                    kwargs[key] = True
                else:
                    kwargs[key] = match.group('value').strip()
            else:
                if item in DEVICES_DATA:
                    kwargs['device'] = item
                else:
                    if not kwargs.get('device', ''):
                        kwargs['device'] = item

        DEVICES_DATA.view(**kwargs)
        sys.exit(0)


def show_info(options):
    if options.command == 'info':
        from platform import uname, python_version
        from gtunrealdevice.config import Data
        lst = [
            Data.main_app_text,
            'Platform: {0.system} {0.release} - Python {1}'.format(
                uname(), python_version()
            ),
            '--------------------',
            'Dependencies:'
        ]

        for pkg in Data.get_dependency().values():
            lst.append('  + Package: {0[package]}'.format(pkg))
            lst.append('             {0[url]}'.format(pkg))

        lst.append('--------------------')

        lst.append('Devices Info:')
        lst.extend(['  - Location: {}'.format(fn) for fn in DEVICES_DATA.filenames])
        lst.append('  - Total devices: {}'.format(len(DEVICES_DATA)))

        lst.append('--------------------')

        lst.append(SerializedFile.get_info_text())

        Printer.print(lst)
        sys.exit(0)


class Cli:
    """gtunrealdevice console CLI application."""
    prog = 'gtunrealdevice'
    prog_fn = 'geeks-trident-unreal-device-app'
    commands = ['app', 'check', 'configure', 'connect', 'destroy',
                'dependency', 'disconnect', 'execute', 'gui', 'info', 'load',
                'reconnect', 'save', 'update', 'version', 'view']

    def __init__(self):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            usage='%(prog)s [options] command operands',
            description='%(prog)s application',
        )

        parser.add_argument(
            '-v', '--version', action='version',
            version='%(prog)s v{}'.format(version)
        )

        parser.add_argument(
            'command', type=str,
            help='command must be either app, check, configure, connect,'
                 'destroy, dependency, disconnect, execute, gui, info, load, '
                 'reconnect, save, update, version, or view'
        )
        parser.add_argument(
            'operands', nargs='*', type=str,
            help='operands are a list of data such as command line and output'
        )

        self.parser = parser
        self.options = self.parser.parse_args()
        self.kwargs = dict()

    def validate_command(self):
        """Validate argparse `options.command`.

        Returns
        -------
        bool: show ``self.parser.print_help()`` and call ``sys.exit(1)`` if
        command is not  app, check, configure, connect, dependency, destroy,
        disconnect, execute, gui, info, load, reconnect,
        save, update, version, or view, otherwise, return True
        """
        self.options.command = self.options.command.lower()

        if self.options.command in self.commands:
            return True
        self.parser.print_help()
        sys.exit(1)

    def run(self):
        """Take CLI arguments, parse it, and process."""
        self.validate_command()
        run_gui_application(self.options)
        show_dependency(self.options)
        show_version(self.options)
        show_info(self.options)
        show_device_info(self.options)

        # device action
        do_device_connect(self.options)
        do_device_disconnect(self.options)
        do_device_execute(self.options)
        do_device_configure(self.options)


def execute():
    """Execute gtunrealdevice console CLI."""
    app = Cli()
    app.run()
