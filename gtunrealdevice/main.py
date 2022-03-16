"""Module containing the logic for the gtunrealdevice entry-points."""

import sys
import argparse

from gtunrealdevice.application import Application
from gtunrealdevice.config import version


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


class Cli:
    """gtunrealdevice console CLI application."""
    prog = 'gtunrealdevice'
    prog_fn = 'geeks-trident-unreal-device-app'
    commands = ['app', 'check', 'config', 'create', 'dependency',
                'execute', 'gui', 'info', 'load', 'reset', 'version']

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
            help='command must be either app, check, config, dependency, '
                 'execute, gui, info, load, reset, or version'
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
        command is not  app, check, config, dependency, execute, gui, info,
        load, reset, or version, otherwise, return True
        """
        self.options.command = self.options.command.lower()

        if self.options.command in self.commands:
            return True
        self.parser.print_help()
        sys.exit(1)
        return True

    def run(self):
        """Take CLI arguments, parse it, and process."""
        self.validate_command()
        run_gui_application(self.options)


def execute():
    """Execute gtunrealdevice console CLI."""
    app = Cli()
    app.run()
