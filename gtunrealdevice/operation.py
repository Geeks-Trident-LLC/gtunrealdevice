"""Module containing the logic for unreal device operation"""

import sys
import re

from gtunrealdevice import UnrealDevice
from gtunrealdevice.utils import Printer
from gtunrealdevice.core import DEVICES_DATA
from gtunrealdevice.serialization import SerializedFile

from gtunrealdevice.usage import validate_usage
from gtunrealdevice.usage import show_usage


def do_device_connect(options):
    if options.command == 'connect':
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
                         'Use reload for a new connection.']
                    ))
                    sys.exit(0)
                else:
                    instance.connect(testcase=testcase)
                    SerializedFile.add_instance(host_addr, instance)
                    sys.exit(0)

            try:
                instance = UnrealDevice(host_addr)
                instance.connect(testcase=testcase)
                SerializedFile.add_instance(host_addr, instance)
                sys.exit(0)
            except Exception as ex:
                failure = '{}: {}'.format(type(ex).__name__, ex)
                print(failure)
                sys.exit(1)
        else:
            show_usage(options.command)


def do_device_disconnect(options):
    if options.command == 'disconnect':
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


def do_device_destroy(options):
    if options.command == 'destroy':
        validate_usage(options.command, options.operands)
        if len(options.operands) == 1:
            host_addr = options.operands[0]

            if host_addr not in DEVICES_DATA:
                for addr, node in DEVICES_DATA.items():
                    if node.get('name') == host_addr:
                        host_addr = addr
                        break

            result = SerializedFile.remove_instance(host_addr)
            print(SerializedFile.message)
            sys.exit(int(result))
        else:
            show_usage(options.command)


def do_device_execute(options):
    if options.command == 'execute':
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


def do_device_configure(options):
    if options.command == 'configure':
        validate_usage(options.command, options.operands)

        data = ' '.join(options.operands).strip()
        pattern = r'(?P<host_addr>\S+::)? *(?P<cfg_ref>.+)'
        match = re.match(pattern, data)
        if match:
            host_addr = match.group('host_addr') or ''
            cfg_ref = match.group('cfg_ref').strip()

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

            instance = SerializedFile.get_instance(host_addr)
            if instance:
                if instance.is_connected:
                    instance.configure(cfg_ref)
                    sys.exit(0)
                else:
                    fmt = 'CANT configure because {} is disconnected.'
                    print(fmt.format(host_addr))
                    sys.exit(0)
            else:
                fmt = 'CANT configure because {} has not connected.'
                print(fmt.format(host_addr))
                sys.exit(0)
        else:
            show_usage(options.command)


def do_device_reload(options):
    if options.command == 'reload':
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

            try:
                reload_data = '\n'.join([
                    'Reloading "{}" device ...'.format(host_addr),
                    '...',
                    'Closing all applications ... Application are closed.',
                    'Unload device drivers ... Unload completed',
                    '... ',
                    'Booting "{}" device ...'.format(host_addr),
                    '...'
                    'Checking memory ... memory tests are PASSED.',
                    'Loading device drivers ... Device drivers are loaded.',
                    '...',
                    'System is ready for login.'
                ])
                instance = UnrealDevice(host_addr)
                instance.reconnect(testcase=testcase, reload_data=reload_data)
                SerializedFile.add_instance(host_addr, instance)
                sys.exit(0)
            except Exception as ex:
                failure = '{}: {}'.format(type(ex).__name__, ex)
                print(failure)
                sys.exit(1)
        else:
            show_usage(options.command)
