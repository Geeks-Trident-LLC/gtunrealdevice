"""Module containing the logic for console command line usage"""

import sys

from gtunrealdevice.utils import Printer
from gtunrealdevice.utils import Misc


class ConfigureUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Configure Usage'),
        'unreal-device configure <cfg_reference>',
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>'
    ])
    other_usage = '\n'.join([
        Printer.get('Unreal Device Configure Usage'),
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>'
    ])


class ConnectUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Connect Usage'),
        'unreal-device connect <host_address>',
        'unreal-device connect <host_address> <testcase>',
        'unreal-device connect <host_name>',
        'unreal-device connect <host_name> <testcase>'
    ])


class DisconnectUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Disconnect Usage'),
        'unreal-device disconnect <host_address>',
        'unreal-device disconnect <host_name>',
    ])


class DestroyUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Destroy/Release Usage'),
        'unreal-device destroy <host_address>',
        'unreal-device destroy <host_name>',
        'unreal-device release <host_address>',
        'unreal-device release <host_name>',
    ])

class ReleaseUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Destroy/Release Usage'),
        'unreal-device destroy <host_address>',
        'unreal-device destroy <host_name>',
        'unreal-device release <host_address>',
        'unreal-device release <host_name>',
    ])


class ExecuteUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Execute Usage'),
        'unreal-device execute <cmdline>',
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>'
    ])

    other_usage = '\n'.join([
        Printer.get('Unreal Device Execute Usage'),
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>'
    ])


class LoadUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Load Usage'),
        'unreal-device load <filename>',
        'unreal-device load keep <filename>',
    ])


class ReloadUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Reload Usage'),
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
    release = ReleaseUsage


def validate_usage(name, operands):
    result = ''.join(operands) if Misc.is_list_instance(operands) else str(operands)
    if result.strip().lower() == 'usage':
        show_usage(name, exit_code=0)


def show_usage(name, *args, exit_code=None):
    obj = getattr(Usage, name, None)
    if getattr(obj, 'usage', None):
        attr = '_'.join(list(args) + ['usage'])
        print(getattr(obj, attr))
        Misc.is_integer(exit_code) and sys.exit(exit_code)
    else:
        fmt = '*** ErrorUsage: "{}" has not defined or unavailable.'
        print(fmt.format(name))
        sys.exit(1)


def get_global_usage():
    lst = [
        Printer.get('Global Usages'),
        'unreal-device app',
        'unreal-device version',
        'unreal-device info',
        '',
        Printer.get('Info File Usage'),
        'unreal-device view',
        'unreal-device view device::<host_address>',
        'unreal-device view device::<host_address> testcase::<testcase_name>',
        'unreal-device view device::<host_address> cmdlines',
        'unreal-device view device::<host_address> testcases',
        '',
        Printer.get('Loading/Saving Device Info Usage'),
        'unreal-device load <filename>',
        'unreal-device load keep <filename>',
        '',
        Printer.get('Unreal Device Connect Usage'),
        'unreal-device connect <host_address>',
        'unreal-device connect <host_address> <testcase>',
        'unreal-device connect <host_name>',
        'unreal-device connect <host_name> <testcase>',
        '',
        Printer.get('Unreal Device Reload Usage'),
        'unreal-device reload <host_address>',
        'unreal-device reload <host_address> <testcase>',
        'unreal-device reload <host_name>',
        'unreal-device reload <host_name> <testcase>',
        '',
        Printer.get('Unreal Device Disconnect Usage'),
        'unreal-device disconnect <host_address>',
        'unreal-device disconnect <host_name>',
        '',
        Printer.get('Unreal Device Destroy/Release Usage'),
        'unreal-device destroy <host_address>',
        'unreal-device destroy <host_name>',
        'unreal-device release <host_address>',
        'unreal-device release <host_name>',
        '',
        Printer.get('Unreal Device Configure Usage'),
        'unreal-device configure <cfg_reference>',
        'unreal-device configure <host_address>::<cfg_reference>',
        'unreal-device configure <host_name>::<cfg_reference>',
        '',
        Printer.get('Unreal Device Execute Usage'),
        'unreal-device execute <cmdline>',
        'unreal-device execute <host_address>::<cmdline>',
        'unreal-device execute <host_name>::<cmdline>',
        '',
    ]

    return '\n'.join(lst)
