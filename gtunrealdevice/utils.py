"""Module containing the logic for utilities."""

import re

from pathlib import Path
from pathlib import PurePath
from datetime import datetime

from textwrap import wrap


class Printer:
    """A printer class.

    Methods
    Printer.get(data, header='', footer='', failure_msg='', width=80, width_limit=20) -> str
    Printer.print(data, header='', footer='', failure_msg='', width=80, width_limit=20, print_func=None) -> None
    """
    @classmethod
    def get(cls, data, header='', footer='',
            width=80, width_limit=20, failure_msg=''):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        width_limit (int): minimum width of displayed text.  Default is 20.
        failure_msg (str): a failure message.  Default is empty.
        """
        headers = str(header).splitlines()
        footers = str(footer).splitlines()
        data = data if Misc.is_sequence_instance(data) else [data]
        lst = []
        result = []

        right_bound = width - 4

        for item in data:
            if width >= width_limit:
                for line in str(item).splitlines():
                    lst.extend(wrap(line, width=right_bound))
            else:
                lst.extend(line.rstrip() for line in str(item).splitlines())
        length = max(len(str(i)) for i in lst + headers + footers)

        if width >= width_limit:
            length = right_bound if right_bound > length else length

        result.append('+-{}-+'.format('-' * length))
        if header:
            for item in headers:
                result.append('| {} |'.format(item.ljust(length)))
            result.append('+-{}-+'.format('-' * length))

        for item in lst:
            result.append('| {} |'.format(item.ljust(length)))
        result.append('+-{}-+'.format('-' * length))

        if footer:
            for item in footers:
                result.append('| {} |'.format(item.ljust(length)))
            result.append('+-{}-+'.format('-' * length))

        if failure_msg:
            result.append(failure_msg)

        txt = '\n'.join(result)
        return txt

    @classmethod
    def print(cls, data, header='', footer='',
              width=80, width_limit=20, failure_msg='', print_func=None):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        width_limit (int): minimum width of displayed text.  Default is 20.
        failure_msg (str): a failure message.  Default is empty.
        print_func (function): a print function.  Default is None.
        """

        txt = Printer.get(data, header=header, footer=footer,
                          failure_msg=failure_msg, width=width,
                          width_limit=width_limit)

        print_func = print_func if callable(print_func) else print
        print_func(txt)

    @classmethod
    def get_message(cls, fmt, *args, style='format', prefix=''):
        """Get a message

        Parameters
        ----------
        fmt (str): string format.
        args (tuple): list of parameters for string interpolation.
        style (str): either format or %.
        prefix (str): a prefix.

        Returns
        -------
        str: a message.
        """

        if args:
            message = fmt.format(*args) if style == 'format' else fmt % args
        else:
            message = fmt

        message = '{} {}'.format(prefix, message) if prefix else message
        return message

    @classmethod
    def print_message(cls, fmt, *args, style='format', prefix='', print_func=None):
        """Print a message

        Parameters
        ----------
        fmt (str): string format.
        args (tuple): list of parameters for string interpolation.
        style (str): either format or %.
        prefix (str): a prefix.
        print_func (function): a print function.
        """
        message = cls.get_message(fmt, *args, style=style, prefix=prefix)
        print_func = print_func if callable(print_func) else print
        print_func(message)

    @classmethod
    def print_unreal_device_msg(cls, fmt, *args, style='format', print_func=None):
        """Print a message

        Parameters
        ----------
        fmt (str): string format.
        args (tuple): list of parameters for string interpolation.
        style (str): either format or %.
        print_func (function): a print function.
        """
        message = cls.get_message(fmt, *args, style=style, prefix='UnrealDeviceMessage:')
        print_func = print_func if callable(print_func) else print
        print_func(message)


class File:
    message = ''

    @classmethod
    def is_exist(cls, filename):
        """Check file existence

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if existed, otherwise False
        """
        file_obj = Path(filename)
        return file_obj.exists()

    @classmethod
    def create(cls, filename, showed=True):
        """Check file existence

        Parameters
        ----------
        filename (str): a file name
        showed (bool): showing the message of creating file

        Returns
        -------
        bool: True if created, otherwise False
        """
        filename = cls.get_path(str(filename).strip())
        if cls.is_exist(filename):
            cls.message = 'File is already existed.'
            return True

        try:
            file_obj = Path(filename)
            if not file_obj.parent.exists():
                file_obj.parent.mkdir(parents=True, exist_ok=True)
            file_obj.touch()
            fmt = '{:%Y-%m-%d %H:%M:%S.%f} - {} file is created.'
            showed and print(fmt.format(datetime.now(), filename))
            cls.message = '{} file is created.'.format(filename)
            return True
        except Exception as ex:
            cls.message = '{}: {}'.format(type(ex).__name__, ex)
            return False

    @classmethod
    def get_path(cls, *args, is_home=False):
        """Create a file path

        Parameters
        ----------
        args (tuple): a list of file items
        is_home (bool): True will include Home directory.  Default is False.

        Returns
        -------
        str: a file path.
        """
        lst = [Path.home()] if is_home else []
        lst.extend(list(args))
        file_path = str(Path(PurePath(*lst)).expanduser().absolute())
        return file_path

    @classmethod
    def get_dir(cls, file_path):
        """get directory from existing file path

        Parameters
        ----------
        file_path (string): file path

        Returns
        -------
        str: directory
        """
        file_obj = Path(file_path).expanduser().absolute()
        if file_obj.is_dir():
            return str(file_obj)
        elif file_obj.is_file():
            return str(file_obj.parent)
        else:
            fmt = 'FileNotFoundError: No such file or directory "{}"'
            cls.message = fmt.format(file_path)
            return ''

    @classmethod
    def get_content(cls, file_path):
        """get content of file

        Parameters
        ----------
        file_path (string): file path

        Returns
        -------
        str: content of file
        """
        filename = cls.get_path(file_path)
        try:
            with open(filename) as stream:
                content = stream.read()
                return content
        except Exception as ex:
            cls.message = '{}: {}'.format(type(ex).__name__, ex)
            return ''

    @classmethod
    def save(cls, filename, data):
        """Create a file path

        Parameters
        ----------
        filename (str): filename
        data (str): data.

        Returns
        -------
        bool: True if successfully saved, otherwise, False
        """
        try:
            if Misc.is_list_instance(data):
                content = '\n'.join(str(item) for item in data)
            else:
                content = str(data)

            filename = cls.get_path(filename)
            if not cls.create(filename):
                return False

            file_obj = Path(filename)
            file_obj.touch()
            file_obj.write_text(content)
            cls.message = 'Successfully saved data to "{}" file'.format(filename)
            return True
        except Exception as ex:
            cls.message = '{}: {}'.format(type(ex).__name__, ex)
            return False


class Misc:
    @classmethod
    def is_dict_instance(cls, obj):
        return isinstance(obj, dict)

    @classmethod
    def is_list_instance(cls, obj):
        return isinstance(obj, list)

    @classmethod
    def is_sequence_instance(cls, obj):
        return isinstance(obj, (list, tuple, set))

    @classmethod
    def is_integer(cls, obj):
        return isinstance(obj, int)

    @classmethod
    def is_boolean(cls, obj):
        return isinstance(obj, bool)

    @classmethod
    def is_float(cls, obj):
        return isinstance(obj, float)

    @classmethod
    def is_string(cls, obj):
        return isinstance(obj, str)


class DictObject(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if re.match(r'(?i)[a-z]\w*', key):
                setattr(self, key, value)


class MiscDevice:
    @classmethod
    def parse_cmdline(cls, data):
        data = str(data)
        pattern = r'(?i)(?P<host>[a-z]([\w-]*[a-z0-9])*::)? *(?P<cmdline>.+)'
        m = re.match(pattern, data)
        if m:
            host, cmdline = m.group('host'), m.group('cmdline')
            if host:
                host = host.strip(':')
                return DictObject(host=host, cmdline=cmdline)
            else:
                return DictObject(host='', cmdline=data)
        else:
            return DictObject(host='', cmdline=data)
