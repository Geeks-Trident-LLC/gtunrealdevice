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
        'unreal-device connect <host_name> <testcase>',
        'unreal-device connect {1, 2, 3, 4, or 5}',
    ])

    example_usage = '\n'.join([
        Printer.get('Unreal Device Connect Example'),
        'unreal-device connect example 1',
        'unreal-device connect example 2',
        'unreal-device connect example 3',
        'unreal-device connect example 4',
        'unreal-device connect example 5',
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


class InfoUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Information Usage'),
        'unreal-device info',
        'unreal-device info all',
        'unreal-device info dependency',
        'unreal-device info device',
        'unreal-device info serialization',
        'unreal-device info sample_devices_info'
    ])


class LoadUsage:
    usage = '\n'.join([
        Printer.get('Unreal Device Load Usage'),
        'unreal-device load <filename>',
        'unreal-device load keep <filename>',
        'unreal-device load example 1',
    ])

    example_usage = '\n'.join([
        Printer.get('Unreal Device Load Example'),
        'unreal-device load example 1',
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
    info = InfoUsage
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
        'unreal-device info all',
        'unreal-device info dependency',
        'unreal-device info device',
        'unreal-device info serialization',
        'unreal-device info sample_devices_info',
        '',
        Printer.get('Viewing devices_info.yaml Usage'),
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
