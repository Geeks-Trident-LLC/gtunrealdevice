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


class DestroyUsage:
    usage = '\n'.join([
        'destroy syntax:',
        '---------------',
        'unreal-device destroy <host_address>',
        'unreal-device destroy <host_name>',
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


class LoadUsage:
    usage = '\n'.join([
        'load syntax:',
        '---------------',
        'unreal-device load <filename>',
        'unreal-device load keep <filename>',
    ])


class ReloadUsage:
    usage = '\n'.join([
        'reload syntax:',
        '--------------',
        'unreal-device reload <host_address>',
        'unreal-device reload <host_address> <testcase>',
        'unreal-device reload <host_name>',
        'unreal-device reload <host_name> <testcase>'
    ])


class Usage:
    configure = ConfigureUsage
    connect = ConnectUsage
    disconnect = DisconnectUsage
    destroy = DestroyUsage
    execute = ExecuteUsage
    load = LoadUsage
    reload = ReloadUsage


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


def get_global_usage():
    lst = [
        Printer.get('Global Usages', width=60),
        'unreal-device app',
        'unreal-device version',
        'unreal-device info',
        '',
        Printer.get('Device Info File Usage', width=60),
        'unreal-device view',
        'unreal-device view device::<host_address>',
        'unreal-device view device::<host_address> testcase::<testcase_name>',
        'unreal-device view device::<host_address> cmdlines',
        'unreal-device view device::<host_address> testcases',
        '',
        Printer.get('Loading/Saving Device Info Usage', width=60),
        'unreal-device load <filename>',
        'unreal-device load keep <filename>',
        '',
        Printer.get('Device Connect Usage', width=60),
        'unreal-device connect <host_address>',
        'unreal-device connect <host_address> <testcase>',
        'unreal-device connect <host_name>',
        'unreal-device connect <host_name> <testcase>',
        '',
        Printer.get('Device Reload Usage', width=60),
        'unreal-device reload <host_address>',
        'unreal-device reload <host_address> <testcase>',
        'unreal-device reload <host_name>',
        'unreal-device reload <host_name> <testcase>',
        '',
        Printer.get('Device Disconnect Usage', width=60),
        'unreal-device disconnect <host_address>',
        'unreal-device disconnect <host_name>',
        '',
        Printer.get('Device Destroy Usage', width=60),
        'unreal-device destroy <host_address>',
        'unreal-device destroy <host_name>',
        '',
        Printer.get('Device Configure Usage', width=60),
        'unreal-device configure <cfg_reference>',
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>',
        '',
        Printer.get('Device Execute Usage', width=60),
        'unreal-device execute <cmdline>',
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>',
        '',
    ]

    return '\n'.join(lst)