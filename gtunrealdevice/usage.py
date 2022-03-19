"""Module containing the logic for console command line usage"""

import sys

from gtunrealdevice.utils import Printer


class ConfigureUsage:
    usage = '\n'.join([
        'configure syntax:',
        '-----------------',
        'unreal-device configure <cfg_reference>',
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>'
    ])
    other_usage = '\n'.join([
        'configure syntax:',
        '-----------------',
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>'
    ])


class ConnectUsage:
    usage = '\n'.join([
        'connect syntax:',
        '---------------',
        'unreal-device connect <host_address>',
        'unreal-device connect <host_address> <testcase>',
        'unreal-device connect <host_name>',
        'unreal-device connect <host_name> <testcase>'
    ])


class DisconnectUsage:
    usage = '\n'.join([
        'disconnect syntax:',
        '------------------',
        'unreal-device disconnect <host_address>',
        'unreal-device disconnect <host_name>',
    ])


class ExecuteUsage:
    usage = '\n'.join([
        'execute syntax:',
        '---------------',
        'unreal-device execute <cmdline>',
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>'
    ])

    other_usage = '\n'.join([
        'execute syntax:',
        '---------------',
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>'
    ])


class Usage:
    configure = ConfigureUsage
    connect = ConnectUsage
    disconnect = DisconnectUsage
    execute = ExecuteUsage


def validate_usage(name, operands):
    result = ''.join(operands) if isinstance(operands, list) else str(operands)
    if result.strip().lower() == 'usage':
        show_usage(name)


def show_usage(name, *args):
    obj = getattr(Usage, name, None)
    if getattr(obj, 'usage', None):
        attr = '_'.join(list(args) + ['usage'])
        Printer.print(getattr(obj, attr))
        sys.exit(0)
    else:
        fmt = '***Usage of "{}" has not defined or unavailable.'
        print(fmt.format(name))
        sys.exit(1)

