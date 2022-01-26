import yaml


class DevicesData(dict):
    def __init__(self):
        data = yaml.load(open(__name__), Loader=yaml.SafeLoader)
        self.update(data)


DEVICESDATA = DevicesData()


class URDevice:
    def __init__(self, address, **kwargs):
        self.address = address
        self.__dict__.update(**kwargs)
        self._is_connected = True

        if address in DEVICESDATA:
            self.data = DEVICESDATA.get(address)
        else:
            raise Exception('TODO: Need exception for this case')

    @property
    def is_connected(self):
        return self._is_connected

    def execute(self, cmdline='', cli='', **kwarg):
        cmdline = cmdline or cli
        if self.is_connected:
            output = self.data.get(cmdline)
            print(output)
            return output
        else:
            raise Exception('TODO: Need exception for this case')

    def disconnect(self):
        self._is_connected = False


def connect(address, **kwargs):
    device = URDevice(address, **kwargs)
    return device


def disconnect(device):
    device.disconnect()


def execute(device, cmdline='', cli='', **kwargs):
    output = device(cmdline=cmdline, cli=cli, **kwargs)
    return output


def configure(device, config='', **kwargs):
    pass


def send(device, data='', **kwargs):
    pass


def sendline(device, cmdline='', cli='', **kwargs):
    pass

