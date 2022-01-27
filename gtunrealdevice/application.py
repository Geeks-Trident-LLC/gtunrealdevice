"""Module containing the logic for the gtunrealdevice application."""

from gtunrealdevice import version
from gtunrealdevice import edition


__version__ = version
__edition__ = edition


class Application:
    def run(self):
        """Launch gtunrealdevice application."""
        data = """
            +--------------------------------------------------------------------------------------+ 
            | {:84} |
            | Please use any text editor to edit ~/.geekstrident/gtunrealdevice/devices_info.yaml. |
            | The structure of devices_info.yaml provides and explains on                          |
            | https://github.com/Geeks-Trident-LLC/gtunrealdevice/blob/develop/README.md           |
            +--------------------------------------------------------------------------------------+
            | Geeks Trident team will announce when GUI application will be available.             |
            +--------------------------------------------------------------------------------------+
        """.format('GTUnrealDevice version {} {}'.format(version, edition))
        from textwrap import dedent
        import sys
        print(dedent(data))
        sys.exit(0)


def execute():
    """Launch gtunrealdevice application."""
    app = Application()
    app.run()

