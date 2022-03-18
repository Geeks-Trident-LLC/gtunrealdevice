"""Module containing the logic for URDevice."""
import re

import yaml
import functools
from os import path

from gtunrealdevice.config import Data
from gtunrealdevice.exceptions import WrapperError
from gtunrealdevice.exceptions import DevicesInfoError
from gtunrealdevice.exceptions import URDeviceConnectionError
from gtunrealdevice.exceptions import URDeviceOfflineError

from gtunrealdevice.utils import Printer


def check_active_device(func):
    """Wrapper for URDevice methods.
    Parameters
    ----------
    func (function): a callable function

    Returns
    -------
    function: a wrapper function

    Raises
    ------
    WrapperError: raise exception when decorator is incorrectly used
    URDeviceOfflineError: raise exception when unreal device is offline
    """
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        """A Wrapper Function"""
        if args:
            device = args[0]
            if isinstance(device, URDevice):
                if device.is_connected:
                    result = func(*args, **kwargs)
                    return result
                else:
                    fmt = '{} device is offline.'
                    raise URDeviceOfflineError(fmt.format(device.name))
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
                data = yaml.load(content, Loader=yaml.SafeLoader)
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

        with open(path.expanduser(filename)) as stream:
            filename not in self.filenames and self.filenames.append(filename)
            content = stream.read()
            if content.strip():
                data = yaml.load(content, Loader=yaml.SafeLoader)
                if isinstance(data, dict):
                    self.clear()
                    self.update(data)
                else:
                    fmt = '{} file has an invalid format.  Check with developer.'
                    raise DevicesInfoError(fmt.format(filename))

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


class URDevice:
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
    disconnect(**kwargs) -> bool
    execute(cmdline, **kwargs) -> str
    configure(config, **kwargs) -> str

    Raises
    ------
    URDeviceConnectionError: raise exception if device can not connect
    """
    def __init__(self, address, name='', **kwargs):
        self.address = str(address).strip()
        self.name = str(name).strip() or self.address
        self.__dict__.update(**kwargs)
        self._is_connected = False
        self.data = None
        self.table = dict()

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
            if kwargs.get('showed', True):
                login_result = self.data.get('login')
                print(login_result)
            return self.is_connected
        else:
            fmt = '{} is unavailable for connection.'
            raise URDeviceConnectionError(fmt.format(self.name))

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
            msg = '{} is disconnected.'.format(self.name)
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
        if hasattr(self, 'testcase'):
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

        if kwargs.get('showed', True):
            print(str(output))
        return str(output)

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
        result = self.data.get(config, '')
        if kwargs.get('showed', True):
            print(result)
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
    URDevice: an unreal device instance.
    """
    device = URDevice(address, name=name, **kwargs)
    return device


def connect(device, **kwargs):
    """Connect an unreal device

    Parameters
    ----------
    device (URDevice): an Unreal device instance
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
    device (URDevice): an Unreal device instance
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
    device (URDevice): an Unreal device instance
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
    device (URDevice): an Unreal device instance
    config (str): configuration data for device
    kwargs (dict): keyword arguments

    Returns
    -------
    str: result of configuration
    """
    result = device.configure(config, **kwargs)
    return result
