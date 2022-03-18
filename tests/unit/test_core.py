import pytest
from os import path
from gtunrealdevice import UnrealDevice

from gtunrealdevice.core import DEVICES_DATA
DEVICES_DATA.load(path.join(path.dirname(__file__), 'data/devices_info.yaml'))


class TestUnrealDevice:
    @pytest.mark.parametrize(
        ('ip_address', 'device_name'),
        [
            ('1.1.1.1', 'device1'),
        ]
    )
    def test_initialization(self, ip_address, device_name):
        device = UnrealDevice(ip_address, name=device_name)
        assert isinstance(device, UnrealDevice)

    @pytest.mark.parametrize(
        ('ip_address', 'device_name', 'status'),
        [
            ('1.1.1.1', 'device1', True),
        ]
    )
    def test_connect(self, ip_address, device_name, status):
        device = UnrealDevice(ip_address, name=device_name)
        connection_status = device.connect(is_timestamp=False)
        assert connection_status == status

    @pytest.mark.parametrize(
        ('ip_address', 'device_name', 'status'),
        [
            ('1.1.1.1', 'device1', False),
        ]
    )
    def test_disconnect(self, ip_address, device_name, status):
        device = UnrealDevice(ip_address, name=device_name)
        device.connect(is_timestamp=False)
        connection_status = device.disconnect(is_timestamp=False)
        assert connection_status == status

    @pytest.mark.parametrize(
        ('ip_address', 'device_name', 'cmdline', 'iteration', 'expected_output'),
        [
            ('1.1.1.1', 'device1', 'show version', 1, 'version is 2.0.1'),
            ('1.1.1.1', 'device1', 'show version', 2, 'version is 2.0.2'),
            ('1.1.1.1', 'device1', 'show version', 3, 'version is 2.0.1'),
            ('1.1.1.1', 'device1', 'show ver', 1, 'version is 2.0.1 other output of show version'),
            ('1.1.1.1', 'device1', 'show ver', 2, 'version is 2.0.1 other output of show version'),
        ]
    )
    def test_common_execute(self, ip_address, device_name, cmdline, iteration, expected_output):
        device = UnrealDevice(ip_address, name=device_name)
        device.connect(is_timestamp=False)
        for _ in range(iteration):
            output = device.execute(cmdline, is_timestamp=False)

        assert output == expected_output

    @pytest.mark.parametrize(
        ('ip_address', 'device_name', 'testcase', 'cmdline', 'iteration', 'expected_output'),
        [
            ('1.1.1.1', 'device1', 'test1', 'show version', 1, 'version is 2.0.1 from test case 1'),
            ('1.1.1.1', 'device1', 'test1', 'show version', 2, 'version is 2.0.2 from test case 1'),
            ('1.1.1.1', 'device1', 'test1', 'show version', 3, 'version is 2.0.1 from test case 1'),
            ('1.1.1.1', 'device1', 'test1', 'show ver', 1, 'version is 2.0.1 other output of show version'),
            ('1.1.1.1', 'device1', 'test1', 'show ver', 2, 'version is 2.0.1 other output of show version'),
        ]
    )
    def test_testcase_execute(self, ip_address, device_name, testcase,
                              cmdline, iteration, expected_output):
        device = UnrealDevice(ip_address, name=device_name)
        device.connect(is_timestamp=False, testcase=testcase)
        for _ in range(iteration):
            output = device.execute(cmdline, is_timestamp=False)

        assert output == expected_output
