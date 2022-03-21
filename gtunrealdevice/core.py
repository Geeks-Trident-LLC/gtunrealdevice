"""Module containing the logic for UnrealDevice."""
import re

import yaml
import functools
from os import path
from datetime import datetime
from textwrap import dedent

from gtunrealdevice.config import Data
from gtunrealdevice.exceptions import WrapperError
from gtunrealdevice.exceptions import DevicesInfoError
from gtunrealdevice.exceptions import UnrealDeviceConnectionError
from gtunrealdevice.exceptions import UnrealDeviceOfflineError

from gtunrealdevice.utils import Printer


def check_active_device(func):
    """Wrapper for UnrealDevice methods.
    Parameters
    ----------
    func (function): a callable function

    Returns
    -------
    function: a wrapper function

    Raises
    ------
    WrapperError: raise exception when decorator is incorrectly used
    UnrealDeviceOfflineError: raise exception when unreal device is offline
    """
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        """A Wrapper Function"""
        if args:
            device = args[0]
            if isinstance(device, UnrealDevice):
                if device.is_connected:
                    result = func(*args, **kwargs)
                    return result
                else:
                    fmt = '{} device is offline.'
                    raise UnrealDeviceOfflineError(fmt.format(device.name))
            else:
                fmt = 'Using invalid decorator for this instance "{}"'
                raise WrapperError(fmt.format(type(device)))
        else:
            raise WrapperError('Using invalid decorator')
    return wrapper_func


class DevicesData(dict):
    """Devices Data class

    Methods
    load_default() -> None
    load(filename) -> None
    """
    def __init__(self):
        super().__init__()
        self.filenames = [Data.devices_info_filename]
        self.message = ''

    def load_default(self):
        """Load devices info from ~/.geekstrident/gtunrealdevice/devices_info.yaml

        Raises
        ------
        DevicesInfoError: raise exception if devices_info_file contains invalid format
        """
        if not Data.is_devices_info_file_exist():
            Data.create_devices_info_file()
        with open(Data.devices_info_filename) as stream:
            content = stream.read()
            if content.strip():
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    self.clear()
                    self.update(data)
                else:
                    fmt = '{} file has an invalid format.  Check with developer.'
                    raise DevicesInfoError(fmt.format(Data.devices_info_filename))

    def load(self, filename):
        """Load devices info from user provided filename

        Parameters
        ----------
        filename (str): a file name

        Raises
        ------
        DevicesInfoError: raise exception if devices_info_file contains invalid format
        """

        is_valid = self.is_valid_file(filename)
        if not is_valid:
            raise DevicesInfoError(self.message)

        with open(path.expanduser(filename)) as stream:
            filename not in self.filenames and self.filenames.append(filename)
            node = yaml.safe_load(stream)
            self.update(node)

    def save(self, filename=''):
        """Save device info to filename

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if filename is successfully saved, otherwise, False.
        """
        filename = filename or Data.devices_info_filename

        with open(path.expanduser(filename), 'w') as stream:
            self and yaml.safe_dump(dict(self), stream)

    def is_valid_file(self, filename):
        """Check filename

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if filename has proper format, otherwise, False.
        """
        try:
            with open(path.expanduser(filename)) as stream:
                content = stream.read().strip()
                if not content:
                    self.message = '"{}" file is empty.'.format(filename)
                    return False

                is_valid = self.is_valid_structure(content)
                return is_valid
        except Exception as ex:
            self.message = '{} - {}'.format(type(ex).__name__, ex)
            return False

    def is_valid_structure(self, data):
        """Check structure of data

        Parameters
        ----------
        data (str): data for device info

        Returns
        -------
        bool: True if data has proper format, otherwise, False.
        """
        node = yaml.safe_load(data)
        if not isinstance(node, dict):
            self.message = 'Invalid device info format.'
            return False

        cmdlines = node.get('cmdlines', None)
        if cmdlines:
            if not isinstance(cmdlines, dict):
                self.message = 'Invalid cmdlines format.'
                return False

            for cmdline in cmdlines:
                if isinstance(cmdline, (list, str)):
                    continue
                self.message = 'Invalid cmdline format.'
                return False

        testcases = node.get('testcases', None)
        if testcases:
            if not isinstance(testcases, dict):
                self.message = 'Invalid testcases format.'
                return False

            for testcase in testcases:
                if isinstance(testcase, dict):
                    continue
                self.message = 'Invalid testcase format.'
                return False

        configs = node.get('configs', None)
        if configs:
            if not isinstance(configs, dict):
                self.message = 'Invalid configs format.'
                return False

        return True

    def get_sample_device_info_format(self):    # noqa
        text = dedent('''
            ####################################################################
            # sample device info                                               #
            # name, login, and testcases nodes are optional                    #
            ####################################################################
            host_address_1:
              name: host_name (optional)
              login: |-
                output_of_login (optional)
              cmdlines:
                cmdline_1: |-
                  line 1 output_of_cmdline_1
                  ...
                  line n output_of_cmdline_1
                cmdline_k_for_multiple_output:
                  - |-
                    line 1 - output_of_cmdline_k
                    ...
                    line n - output_of_cmdline_k
                  - |-
                    line 1 - other_output_of_cmdline_k
                    ...
                    line n - other_output_of_cmdline_k
              testcases:
                name_of_testcase_1:
                  cmdline_1: |-
                    line 1 output_of_cmdline_1_of_testcase_1
                    ...
                    line n output_of_cmdline_1_of_testcase_1
              configs:
                cfg_1: |-
                  line 1 of cfg_1 
                  ...
                  line n of cfg_1
        ''').strip()
        return text

    def get_data(self, data):       # noqa
        pattern = r'(?i) *file(name)?:: *(?P<fn>[^\r\n]*[a-z][^\r\n]*) *$'
        match = re.match(pattern, data)
        if match and len(data.strip()) == 1:
            try:
                with open(match.group('fn')) as stream:
                    result = stream.read()
            except Exception as ex:     # noqa
                result = data
        else:
            result = data
        return result

    def update_command_line(self, cmdline, output, device,
                            testcase='', appended=False):

        output = self.get_data(output)

        if testcase:
            if device in self:
                testcases = self[device].get('testcases', dict())
                if testcase in testcases:
                    if appended:
                        if cmdline in testcases[testcase]:
                            value = testcases[testcase][cmdline]
                            if isinstance(value, list):
                                value.append(output)
                            else:
                                testcases[testcase][cmdline] = [value, output]
                        else:
                            testcases[testcase][cmdline] = output
                    else:
                        testcases[testcase][cmdline] = output
                else:
                    testcases[testcase] = {cmdline: output}
                testcases and self[device].update(testcases=testcases)
            else:
                self[device] = dict(testcases={testcase: {cmdline: output}})
        else:
            if device in self:
                cmdlines = self[device].get('cmdlines', dict())
                if cmdline in cmdlines:
                    if appended:
                        if isinstance(cmdlines[cmdline], list):
                            cmdlines[cmdline].append(output)
                        else:
                            cmdlines[cmdline] = [cmdlines[cmdline], output]
                    else:
                        cmdlines[cmdline] = output
                else:
                    cmdlines[cmdline] = output
                cmdlines and self[device].update(cmdlines=cmdlines)
            else:
                self[device] = dict(cmdlines={cmdline: output})

    def view(self, device='', cmdlines=False, testcase='', testcases=False):
        lst = ['Devices Info:']
        lst.extend(['  - Location: {}'.format(fn) for fn in DEVICES_DATA.filenames])
        lst.append('  - Total devices: {}'.format(len(DEVICES_DATA)))
        Printer.print(lst)

        if not self:
            print('There is zero device.')

        if any([device, cmdlines, testcase, testcases]):
            if device:
                if device in self:
                    tcs = self[device].get('testcases', None)
                    if testcase:
                        if tcs and testcase in tcs:
                            print(yaml.dump(tcs[testcase]))
                        elif tcs and testcase not in tcs:
                            fmt = 'There is no {} test case in {!r} device.'
                            print(fmt.format(testcase, device))
                        else:
                            fmt = 'There is no testcases section in {!r} device.'
                            print(fmt.format(device))
                    else:
                        if testcases or cmdlines:
                            if testcases:
                                if tcs:
                                    print(yaml.dump(tcs))
                                else:
                                    fmt = 'There is no testcases section in {!r} device.'
                                    print(fmt.format(device))
                            else:
                                node = self[device].get('cmdlines', None)
                                if node:
                                    print(yaml.dump(node))
                                else:
                                    fmt = 'There is no cmdlines section in {!r} device.'
                                    print(fmt.format(device))
                        else:
                            print(yaml.dump(self[device]))
                else:
                    print('There is no {!r} device.'.format(device))
            else:
                self and print(yaml.dump(dict(self)))
        else:
            self and print(yaml.dump(dict(self)))


DEVICES_DATA = DevicesData()
DEVICES_DATA.load_default()


class UnrealDevice:
    """Unreal Device class

    Attributes
    ----------
    address (str): an address of device
    name (str): name of device
    kwargs (dict): keyword arguments

    Properties
    ----------
    is_connected -> bool

    Methods
    -------
    connect(**kwargs) -> bool
    reconnect(**kwargs) -> bool
    disconnect(**kwargs) -> bool
    execute(cmdline, **kwargs) -> str
    configure(config, **kwargs) -> str
    render_data(data, is_cfg=False, is_timestamp=True) -> str

    Raises
    ------
    UnrealDeviceConnectionError: raise exception if device can not connect
    """
    def __init__(self, address, name='', **kwargs):
        self.address = str(address).strip()
        self.name = str(name).strip() or self.address
        self.__dict__.update(**kwargs)
        self._is_connected = False
        self.data = None
        self.table = dict()
        self.testcase = ''

    @property
    def is_connected(self):
        """Return device connection status"""
        return self._is_connected

    def connect(self, **kwargs):
        """Connect an unreal device

        Parameters
        ----------
        kwargs (dict): keyword arguments

        Returns
        -------
        bool: connection status
        """
        if self.is_connected:
            return self.is_connected

        if self.address in DEVICES_DATA:
            self.data = DEVICES_DATA.get(self.address)
            self._is_connected = True

            testcase = kwargs.get('testcase', '')
            if testcase:
                if testcase in self.data.get('testcases', dict()):
                    self.testcase = testcase
                else:
                    fmt = '*** "{}" test case is unavailable for this connection ***'
                    print(fmt.format(testcase))

            if kwargs.get('showed', True):
                login_result = self.data.get('login', '')
                if login_result:
                    is_timestamp = kwargs.get('is_timestamp', True)
                    login_result = self.render_data(
                        login_result, is_timestamp=is_timestamp
                    )
                    print(login_result)
            return self.is_connected
        else:
            fmt = '{} is unavailable for connection.'
            raise UnrealDeviceConnectionError(fmt.format(self.name))

    def reconnect(self, **kwargs):
        """Reconnect an unreal device

        Parameters
        ----------
        kwargs (dict): keyword arguments

        Returns
        -------
        bool: connection status
        """
        if self.address in DEVICES_DATA:
            self.data = DEVICES_DATA.get(self.address)
            self._is_connected = True

            testcase = kwargs.get('testcase', '')
            if testcase:
                if testcase in self.data.get('testcases', dict()):
                    self.testcase = testcase
                else:
                    fmt = '*** "{}" test case is unavailable for this reconnection ***'
                    print(fmt.format(testcase))

            if kwargs.get('showed', True):
                reload_txt = self.data.get('reload', '')
                if not reload_txt:
                    reload_txt = kwargs.get('reload_data', '')
                login_txt = self.data.get('login', '')
                reconnect_txt = '{}\n{}'.format(reload_txt, login_txt).strip()
                if reconnect_txt:
                    is_timestamp = kwargs.get('is_timestamp', True)
                    reconnect_txt = self.render_data(
                        reconnect_txt, is_timestamp=is_timestamp
                    )
                    print(reconnect_txt)
            return self.is_connected
        else:
            fmt = '{} is unavailable for reconnection.'
            raise UnrealDeviceConnectionError(fmt.format(self.name))

    def disconnect(self, **kwargs):
        """Disconnect an unreal device

        Parameters
        ----------
        kwargs (dict): keyword arguments

        Returns
        -------
        bool: disconnection status
        """
        self._is_connected = False
        if kwargs.get('showed', True):
            is_timestamp = kwargs.get('is_timestamp', True)
            msg = '{} is disconnected.'.format(self.name)
            msg = self.render_data(msg, is_timestamp=is_timestamp)
            print(msg)
        return self._is_connected

    @check_active_device
    def execute(self, cmdline, **kwargs):
        """Execute command line for an unreal device

        Parameters
        ----------
        cmdline (str): command line
        kwargs (dict): keyword arguments

        Returns
        -------
        str: output of a command line
        """

        data = self.data.get('cmdlines')
        if self.testcase:
            data = self.data.get('testcases').get(self.testcase, data)

        no_output = '*** "{}" does not have output ***'.format(cmdline)
        result = data.get(cmdline, self.data.get('cmdlines').get(cmdline, no_output))
        if not isinstance(result, (list, tuple)):
            output = str(result)
        else:
            index = 0 if cmdline not in self.table else self.table.get(cmdline) + 1
            index = index % len(result)
            self.table.update({cmdline: index})
            output = result[index]

        is_timestamp = kwargs.get('is_timestamp', True)
        output = self.render_data(output, is_timestamp=is_timestamp)
        if kwargs.get('showed', True):
            print(output)
        return output

    @check_active_device
    def configure(self, config, **kwargs):
        """Configure an unreal device

        Parameters
        ----------
        config (str): configuration data for device
        kwargs (dict): keyword arguments

        Returns
        -------
        str: result of configuration
        """
        is_timestamp = kwargs.get('is_timestamp', True)
        result = self.render_data(config, is_cfg=True, is_timestamp=is_timestamp)
        if kwargs.get('showed', True):
            print(result)
        return result

    def render_data(self, data, is_cfg=False, is_timestamp=True):

        if isinstance(data, str):
            lst = data.splitlines()
        else:
            lst = []
            for item in data:
                if isinstance(item, str):
                    lst.extend(item.splitlines())
                else:
                    lst.extend(item)

        if is_cfg:
            prompt = '{}(configure)#'.format(self.name)
            
            for index, item in enumerate(lst):
                if index == 0:
                    continue
                lst[index] = '{} {}'.format(prompt, item)

        if is_timestamp:
            dt = datetime.now()
            fmt = '+++ {:%b %d %Y %T}.{} from "unreal-device" for "{}"'
            timestamp = fmt.format(dt, str(dt.microsecond)[:3], self.name)
            lst.insert(int(is_cfg), timestamp)
        
        result = '\n'.join(lst)
        return result


def create(address, name='', **kwargs):
    """Create an unreal device instance

    Parameters
    ----------
    address (str): address of device
    name (str): device name
    kwargs (dict): keyword arguments

    Returns
    -------
    UnrealDevice: an unreal device instance.
    """
    device = UnrealDevice(address, name=name, **kwargs)
    return device


def connect(device, **kwargs):
    """Connect an unreal device

    Parameters
    ----------
    device (UnrealDevice): an unreal device instance
    kwargs (dict): keyword arguments

    Returns
    -------
    bool: connection status
    """
    result = device.connect(**kwargs)
    return result


def disconnect(device, **kwargs):
    """Disconnect an unreal device

    Parameters
    ----------
    device (UnrealDevice): an unreal device instance
    kwargs (dict): keyword arguments

    Returns
    -------
    bool: disconnection status
    """
    result = device.disconnect(**kwargs)
    return result


def execute(device, cmdline, **kwargs):
    """Execute command line foran unreal device

    Parameters
    ----------
    device (UnrealDevice): an unreal device instance
    cmdline (str): command line
    kwargs (dict): keyword arguments

    Returns
    -------
    str: output of a command line
    """
    output = device.execute(cmdline, **kwargs)
    return output


def configure(device, config, **kwargs):
    """Configure an unreal device

    Parameters
    ----------
    device (UnrealDevice): an unreal device instance
    config (str): configuration data for device
    kwargs (dict): keyword arguments

    Returns
    -------
    str: result of configuration
    """
    result = device.configure(config, **kwargs)
    return result
