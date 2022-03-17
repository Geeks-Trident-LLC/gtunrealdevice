"""Module containing the logic for utilities."""

import re


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
