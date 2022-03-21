"""Module containing the logic for UnrealDevice(s) serialization."""

import yaml
import pickle

from gtunrealdevice.exceptions import SerializedError
from gtunrealdevice.exceptions import InvalidSerializedFile
from gtunrealdevice.exceptions import InvalidSerializedInstance
from gtunrealdevice import UnrealDevice

from gtunrealdevice.config import Data
from gtunrealdevice.utils import File


class SerializedFile:
    filename = Data.serialized_filename
    message = ''

    @classmethod
    def is_file_exist(cls):
        return File.is_exist(cls.filename)

    @classmethod
    def create_file(cls):
        is_created = File.create(cls.filename)
        cls.message = File.message
        return is_created

    @classmethod
    def get_info(cls):
        tbl = dict(filename=cls.filename)
        if cls.is_file_exist():
            tbl.update(existed=True)
            with open(cls.filename) as stream:
                content = stream.read().strip()
                if content:
                    dict_obj = yaml.safe_load(content)
                    if isinstance(dict_obj, dict):
                        tbl.update(dict_obj=dict_obj)
                        for byte_data in dict_obj.values():
                            try:
                                obj = pickle.loads(byte_data)
                                if isinstance(obj, UnrealDevice):
                                    continue
                                type_name = type(obj).__name__
                                fmt = 'Expecting UnrealDevice instance but received {} type'
                                raise InvalidSerializedInstance(fmt.format(type_name))
                            except Exception as ex:
                                raise SerializedError(str(ex))
                        tbl.update(total=len(dict_obj))
                    else:
                        failure = 'Invalid format {}'.format(cls.filename)
                        raise InvalidSerializedFile(failure)
                else:
                    tbl.update(total=0)
        else:
            tbl.update(existed=False)
            tbl.update(total=0)

        lst = ['Serialized Device(s) Info:',
               '  - Location: {}'.format(tbl['filename']),
               '  - Existed: {}'.format('Yes' if tbl['existed'] else 'No'),
               '  - Total serialized instances: {}'.format(tbl['total'])]

        tbl.update(text='\n'.join(lst))
        return tbl

    @classmethod
    def get_info_text(cls):
        tbl = cls.get_info()
        return tbl.get('text')

    @classmethod
    def add_instance(cls, name, node):
        cls.create_file()
        tbl = cls.get_info()
        dict_obj = tbl.get('dict_obj', dict())
        dict_obj.update({name: pickle.dumps(node)})
        with (open(cls.filename, 'w')) as stream:
            yaml.dump(dict_obj, stream)
            fmt = '+++ Successfully added unreal "{}" device.'
            cls.message = fmt.format(name)
            return True

    @classmethod
    def remove_instance(cls, name):
        tbl = cls.get_info()
        if tbl.get('total') == 0:
            fmt = '''*** CANT remove because unreal "{}" device isn't initialized.'''
            cls.message = fmt.format(name)
            return False
        else:
            with open(cls.filename) as read_stream:
                dict_obj = yaml.safe_load(read_stream)
                if name in dict_obj:
                    byte_data = dict_obj.pop(name)
                    instance = pickle.loads(byte_data)
                    instance.is_connected and instance.disconnect()
                    with (open(cls.filename, 'w')) as write_stream:
                        yaml.dump(dict_obj, write_stream)
                    fmt = '+++ Successfully removed unreal {} device.'
                    cls.message = fmt.format(name)
                    return True
                else:
                    fmt = '*** CANT remove because there is no unreal "{}" device.'
                    cls.message = fmt.format(name)
                    return False

    @classmethod
    def check_instance(cls, name, testcase=''):
        tbl = cls.get_info()
        dict_obj = tbl.get('dict_obj', dict())
        if name in dict_obj:
            if testcase:
                instance = pickle.loads(dict_obj.get(name))
                return getattr(instance, 'testcase', '') == testcase
            else:
                return True
        else:
            return False

    @classmethod
    def get_instance(cls, name):
        tbl = cls.get_info()
        dict_obj = tbl.get('dict_obj', dict())
        if name in dict_obj:
            instance = pickle.loads(dict_obj.get(name))
            return instance
        else:
            return None
