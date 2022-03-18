"""Module containing the logic for the gtunrealdevice entry-points."""
import re
import sys
import argparse

from gtunrealdevice.application import Application
from gtunrealdevice.config import version
from gtunrealdevice.core import DEVICES_DATA
from gtunrealdevice.utils import Printer

from gtunrealdevice import URDevice
from gtunrealdevice.serialization import SerializedFile


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


def do_device_connect(options):
    if options.command == 'connect':
        lst = [
            'unreal-device connect syntax:', '-' * 10,
            'unreal-device connect <host_address>',
            'unreal-device connect <host_address> <testcase>',
            'unreal-device connect <host_name>',
            'unreal-device connect <host_name> <testcase>'
        ]
        connect_syntax = '\n'.join(lst)
        total = len(options.operands)
        if total == 1 or total == 2:
            host_addr = options.operands[0]
            testcase = options.operands[1] if total == 2 else ''

            if host_addr not in DEVICES_DATA:
                for addr, node in DEVICES_DATA.items():
                    if node.get('name') == host_addr:
                        host_addr = addr
                        break

            if SerializedFile.check_instance(host_addr, testcase=testcase):
                instance = SerializedFile.get_instance(host_addr)

                if instance.is_connected:
                    Printer.print('\n'.join(
                        ['{} is already connected.'.format(host_addr),
                         'Use reconnect, reload, or reset for a new connection.']
                    ))
                    sys.exit(0)
                else:
                    instance.connect()
                    SerializedFile.add_instance(host_addr, instance)
                    sys.exit(0)

            try:
                instance = URDevice(host_addr, showed=True)
                if testcase:
                    instance.testcase = testcase
                instance.connect()
                SerializedFile.add_instance(host_addr, instance)
                sys.exit(0)
            except Exception as ex:
                failure = '{}: {}'.format(type(ex).__name__, ex)
                print(failure)
                sys.exit(1)
        else:
            Printer.print(connect_syntax)
            sys.exit(1)


def do_device_disconnect(options):
    if options.command == 'disconnect':
        lst = [
            'unreal-device disconnect syntax:', '-' * 10,
            'unreal-device disconnect <host_address>',
            'unreal-device connect <host_name>',
        ]
        disconnect_syntax = '\n'.join(lst)
        if len(options.operands) == 1:
            host_addr = options.operands[0]
            original_addr = host_addr

            if host_addr not in DEVICES_DATA:
                for addr, node in DEVICES_DATA.items():
                    if node.get('name') == host_addr:
                        host_addr = addr
                        break

            instance = SerializedFile.get_instance(host_addr)
            if instance:
                instance.disconnect()
                SerializedFile.add_instance(host_addr, instance)
                sys.exit(0)
            else:
                if host_addr in DEVICES_DATA:
                    fmt = 'CANT disconnect because {} has not connected.'
                    print(fmt.format(original_addr))
                    sys.exit(1)
                else:
                    fmt = 'CANT disconnect because {} is not available.'
                    print(fmt.format(original_addr))
                    sys.exit(1)
        else:
            Printer.print(disconnect_syntax)
            sys.exit(1)


def do_device_execute(options):
    if options.command == 'execute':
        lst = ['unreal-device execute syntax:', '-' * 10,
               'unreal-device execute <cmdline>',
               'unreal-device execute <host_address>::<cmdline>',
               'unreal-device execute <host_name>::<cmdline>']
        execute_syntax = '\n'.join(lst)
        other_execute_syntax = '\n'.join(lst[:1] + lst[2:])

        data = ' '.join(options.operands).strip()
        pattern = r'(?P<host_addr>\S+::)? *(?P<cmdline>.+)'
        match = re.match(pattern, data)
        if match:
            host_addr = match.group('host_addr') or ''
            cmdline = match.group('cmdline').strip()

            if host_addr:
                host_addr = host_addr.strip(':')
                if host_addr not in DEVICES_DATA:
                    for addr, node in DEVICES_DATA.items():
                        if node.get('name') == host_addr:
                            host_addr = addr
                            break
            else:
                if len(DEVICES_DATA) == 1:
                    host_addr = list(DEVICES_DATA)[0]
                else:
                    Printer.print(other_execute_syntax)
                    sys.exit(1)

            instance = SerializedFile.get_instance(host_addr)
            if instance:
                if instance.is_connected:
                    instance.execute(cmdline)
                    sys.exit(0)
                else:
                    fmt = 'CANT execute cmdline because {} is disconnected.'
                    print(fmt.format(host_addr))
                    sys.exit(0)
            else:
                fmt = 'CANT execute cmdline because {} has not connected.'
                print(fmt.format(host_addr))
                sys.exit(0)
        else:
            Printer.print(execute_syntax)
            sys.exit(1)


class Cli:
    """gtunrealdevice console CLI application."""
    prog = 'gtunrealdevice'
    prog_fn = 'geeks-trident-unreal-device-app'
    commands = ['app', 'check', 'configure', 'connect', 'dependency',
                'disconnect', 'execute', 'gui', 'info', 'load',
                'reconnect', 'reset', 'reload', 'save',
                'update', 'version', 'view']

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
                 'dependency, disconnect, execute, gui, info, load, '
                 'reconnect, reset, reload, save, update, '
                 'version, or view'
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
        command is not  app, check, configure, connect, dependency, disconnect,
        execute, gui, info, load, reconnect, reset, reload,
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
        do_device_connect(self.options)
        do_device_disconnect(self.options)
        do_device_execute(self.options)


def execute():
    """Execute gtunrealdevice console CLI."""
    app = Cli()
    app.run()
