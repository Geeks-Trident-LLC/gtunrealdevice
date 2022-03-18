"""Module containing the logic for unreal device operation"""

import sys
import re

from gtunrealdevice import URDevice
from gtunrealdevice.utils import Printer
from gtunrealdevice.core import DEVICES_DATA
from gtunrealdevice.serialization import SerializedFile

from gtunrealdevice.usage import validate_usage
from gtunrealdevice.usage import show_usage


def do_device_connect(options):
    if options.command == 'connect':
        # lst = [
        #     'unreal-device connect syntax:', '-' * 10,
        #     'unreal-device connect <host_address>',
        #     'unreal-device connect <host_address> <testcase>',
        #     'unreal-device connect <host_name>',
        #     'unreal-device connect <host_name> <testcase>'
        # ]
        # connect_syntax = '\n'.join(lst)
        validate_usage(options.command, options.operands)
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
                    instance.connect(testcase=testcase)
                    SerializedFile.add_instance(host_addr, instance)
                    sys.exit(0)

            try:
                instance = URDevice(host_addr)
                instance.connect(testcase=testcase)
                SerializedFile.add_instance(host_addr, instance)
                sys.exit(0)
            except Exception as ex:
                failure = '{}: {}'.format(type(ex).__name__, ex)
                print(failure)
                sys.exit(1)
        else:
            # Printer.print(connect_syntax)
            # sys.exit(1)
            show_usage(options.command)


def do_device_disconnect(options):
    if options.command == 'disconnect':
        # lst = [
        #     'unreal-device disconnect syntax:', '-' * 10,
        #     'unreal-device disconnect <host_address>',
        #     'unreal-device disconnect <host_name>',
        # ]
        # disconnect_syntax = '\n'.join(lst)
        validate_usage(options.command, options.operands)
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
            show_usage(options.command)
            # Printer.print(disconnect_syntax)
            # sys.exit(1)


def do_device_execute(options):
    if options.command == 'execute':
        # lst = ['unreal-device execute syntax:', '-' * 10,
        #        'unreal-device execute <cmdline>',
        #        'unreal-device execute <host_address>::<cmdline>',
        #        'unreal-device execute <host_name>::<cmdline>']
        # execute_syntax = '\n'.join(lst)
        # other_execute_syntax = '\n'.join(lst[:1] + lst[2:])
        validate_usage(options.command, options.operands)

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
                    show_usage(options.command, 'other')
                    # Printer.print(other_execute_syntax)
                    # sys.exit(1)

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
            show_usage(options.command)
            # Printer.print(execute_syntax)
            # sys.exit(1)
