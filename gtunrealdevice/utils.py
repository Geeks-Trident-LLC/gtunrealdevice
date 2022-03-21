"""Module containing the logic for utilities."""

import re
from pathlib import Path
from pathlib import PurePath
from datetime import datetime


class Printer:
    """A printer class.

    Methods
    Printer.get(data, header='', footer='', failure_msg='', width=80) -> str
    Printer.print(data, header='', footer='', failure_msg='', print_func=None) -> None
    """
    @classmethod
    def get(cls, data, header='', footer='', width=80, failure_msg=''):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        failure_msg (str): a failure message.  Default is empty.
        """
        headers = str(header).splitlines()
        footers = str(footer).splitlines()
        data = data if isinstance(data, (list, tuple)) else [data]
        lst = []
        result = []

        left_limit = 20
        left_bound, right_bound = left_limit - 4, width - 4

        if width > left_limit:
            pat = r'(.{%s,%s}\S) +' % (left_bound, right_bound)
        else:
            pat = ''

        for item in data:
            if pat:
                for line in str(item).splitlines():
                    line = line.rstrip()
                    if len(line) > right_bound:
                        line = re.sub(pat, r'\1\n', line)
                        lst.extend(line.splitlines())
                    else:
                        lst.append(line)
            else:
                lst.extend(line.rstrip() for line in str(item).splitlines())
        length = max(len(str(i)) for i in lst + headers + footers)
        if width > left_limit:
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
    def print(cls, data, header='', footer='', width=80, failure_msg='',
              print_func=None):
        """Decorate data by organizing header, data, footer, and failure_msg

        Parameters
        ----------
        data (str, list): a text or a list of text.
        header (str): a header text.  Default is empty.
        footer (str): a footer text.  Default is empty.
        width (int): width of displayed text.  Default is 80.
        failure_msg (str): a failure message.  Default is empty.
        print_func (function): a print function.  Default is None.
        """

        txt = Printer.get(data, header=header, footer=footer,
                          failure_msg=failure_msg, width=width)

        print_func = print_func if callable(print_func) else print
        print_func(txt)


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
    def create(cls, filename):
        """Check file existence

        Parameters
        ----------
        filename (str): a file name

        Returns
        -------
        bool: True if created, otherwise False
        """
        if cls.is_exist(filename):
            cls.message = 'File is already existed.'
            return True

        try:
            file_obj = Path(filename)
            if not file_obj.parent.exists():
                file_obj.parent.mkdir(parents=True, exist_ok=True)
            file_obj.touch()
            fmt = '{:%Y-%m-%d %H:%M:%S.%f} - {} file is created.'
            print(fmt.format(datetime.now(), filename))
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
        return str(PurePath(*lst))
