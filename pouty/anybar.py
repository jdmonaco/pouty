"""
Set the color of your AnyBar widget.
"""

import os
import sys
import socket
import subprocess

from .shell import Shell
from . import debug


BASE_PORT = 1738
COLORS = ( 'white', 'red', 'orange', 'yellow', 'green', 'cyan',
           'blue', 'purple', 'black', 'question', 'exclamation' )


_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


class AnyBar(object):

    """
    An instance of the AnyBar menubar display application.
    """

    _instances = []

    def __init__(self, color=None, port=None, pid=None, singleton=True):
        self.socket = _socket
        self.color = 'white' if color is None else color
        if singleton:
            self.port = BASE_PORT
            running = Shell.pgrep('AnyBar')
            self.pid = running[0] if running else pid
        else:
            self.port = port
            self.pid = pid
        if sys.platform.lower() != 'darwin':
            print(f'Warning: AnyBar not available ({sys.platform})',
                    file=sys.stderr)
            return
        self.start()

    def __str__(self):
        return f'AnyBar(color=\'{self.color}\', port={self.port}, ' \
               f'pid={self.pid})'

    def __repr__(self):
        return str(self)

    @classmethod
    def toggle(cls, color1='green', color2='purple'):
        """
        Toggle the most recent AnyBar instance between two colors.
        """
        if not cls._instances: return
        abar = cls._instances[-1]
        if abar.color not in (color1, color2):
            abar.set_color(color1)
            return
        abar.set_color({color1:color2, color2:color1}[abar.color])

    def start(self):
        """
        Start a new AnyBar instance.
        """
        already = False
        running = Shell.pgrep('AnyBar')
        if self.pid is not None:
            if self.pid in running:
                if self.port is None:
                    self.quit()
                else:
                    already = True
                    debug(f'already running ({self.pid})', prefix='AnyBar')
            else:
                self.pid = self.port = None

        # Set the port based on number of currently running AnyBars
        if not already and self.port is None:
            self.port = BASE_PORT + len(running)

        # Start a new instance of the AnyBar application
        if self.pid is None:
            if Shell.setenv('ANYBAR_PORT', self.port) == 0:
                self.pid = Shell.open_('AnyBar', newinstance=True)
                if self.pid is not None:
                    self.__class__._instances.append(self)
            else:
                debug(f'unable to set port ({self.port})', prefix='AnyBar')

    def quit(self):
        """
        Quit the AnyBar instance.
        """
        res = subprocess.run(['kill', '-HUP', str(self.pid)])
        if res.returncode != 0:
            self.__class__.quit_all()
            self.__class__._instances.clear()
        if self in self.__class__._instances:
            self.__class__._instances.remove(self)
        self.pid = None
        self.port = None

    @classmethod
    def quit_all(cls):
        """
        Quit all running instances of AnyBar.
        """
        insts = cls._instances.copy()
        [abar.quit() for abar in reversed(insts)]
        cls._instances.clear()

        # Kill any remaining instances (e.g., from previous processes)
        Shell.killall('AnyBar')

    def set_color(self, color=None):
        """
        Set the color of the AnyBar widget.

        Valid colors: {}.
        """
        color = self.color if color is None else color
        if self.port is None or self.pid is None:
            print('AnyBar: not running', file=sys.stderr)
            return
        if color not in COLORS:
            raise ValueError("Invalid color: {}".format(color))
        self.socket.sendto(color.encode('utf-8'), ('localhost', self.port))
        self.color = color

    set_color.__doc__ = set_color.__doc__.format(', '.join(["\'%s\'" % c
        for c in COLORS]))
