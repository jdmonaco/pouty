"""
Colorful bash output.
"""

import os
import re
import time
from sys import stdout, stderr, platform

from roto.paths import tilde

from .notifier import Notifier


QUIET_MODE = False
DEBUG_MODE = False
WINDOWS = (platform == 'win32')
DEFAULT_PREFIX_COLOR = 'cyan'
DEFAULT_MSG_COLOR = 'default'


# Terminal color functions

def _color_format(code, text):
    return f'\033[{code}m{text}\033[0m'

def snow(s):      return _color_format("1;37", s)  # white
def white(s):     return _color_format("0;37", s)  # lightgray
def lightgray(s): return _color_format("1;36", s)  # lightcyan
def smoke(s):     return _color_format("1;36", s)  # lightcyan
def dimgray(s):   return _color_format("1;33", s)  # yellow
def gray(s):      return _color_format("1;30", s)  # gray
def cadetblue(s): return _color_format("1;34", s)  # lightblue
def seafoam(s):   return _color_format("1;32", s)  # lightgreen
def cyan(s):      return _color_format("0;36", s)  # cyan
def blue(s):      return _color_format("0;34", s)  # blue
def purple(s):    return _color_format("1;35", s)  # pink
def pink(s):      return _color_format("0;35", s)  # purple
def red(s):       return _color_format("0;31", s)  # red
def orange(s):    return _color_format("1;31", s)  # lightred
def yellow(s):    return _color_format("0;33", s)  # brown
def ochre(s):     return _color_format("0;33", s)  # brown
def green(s):     return _color_format("0;32", s)  # green
def default(s):   return _color_format("", s)      # terminal default


# Synonyms for backwards compatibility

_lightred   = orange
_lightgreen = seafoam
_brown      = yellow
_lightblue  = cadetblue
_lightcyan  = lightgray


# Color name-function mapping

COL_FUNC = {
    'snow'       : snow,
    'white'      : white,
    'lightgray'  : lightgray,
    'smoke'      : smoke,
    'dimgray'    : dimgray,
    'gray'       : gray,
    'cadetblue'  : cadetblue,
    'seafoam'    : seafoam,
    'cyan'       : cyan,
    'blue'       : blue,
    'purple'     : purple,
    'pink'       : pink,
    'red'        : red,
    'orange'     : orange,
    'yellow'     : yellow,
    'ochre'      : ochre,
    'green'      : green,
    'lightred'   : _lightred,
    'lightgreen' : _lightgreen,
    'brown'      : _brown,
    'lightblue'  : _lightblue,
    'lightcyan'  : _lightcyan,
    'default'  : default,
}

COLORS = list(COL_FUNC.keys())

def show_colors():
    for c in COLORS:
        print(COL_FUNC[c](' ' + c.ljust(11) + "\u25a0"*68))


class ConsolePrinter(object):

    """
    A callable console printer with color, log files, and notifications.
    """

    _outputfile = None
    _fd = None
    _timestamp = False
    _hanging = False

    def __init__(self, prefix='', prefix_color=None, message_color=None):
        """Create a colorful callable console printing object.

        Keyword arguments:
        prefix -- default prefix string for console output
        prefix_color -- color name for prefix text
        message_color -- color name for message text
        """
        self._prefix = prefix
        self.set_prefix_color(prefix_color)
        self.set_message_color(message_color)
        self._notifier = None

    @classmethod
    def _isopen(cls):
        return cls._fd is not None and not cls._fd.closed

    @classmethod
    def openfile(cls, newfile=False):
        """Open the currently set output file."""
        if cls._outputfile is None:
            print('No output file has been set', file=sys.stderr)
            return
        if cls._isopen():
            return
        mode = 'w' if newfile else 'a'
        try:
            cls._fd = open(cls._outputfile, mode, 1)
        except IOError:
            cls._outputfile = cls._fd = None
            print('IOError: Could not open {cls._outputfile!r}',
                  file=sys.stderr)

    @classmethod
    def closefile(cls):
        """Close the current output file."""
        if not cls._isopen():
            cls._fd = None
            return
        cls._fd.close()
        cls._fd = None

    @classmethod
    def removefile(cls):
        """Delete the current output file."""
        cls.closefile()
        os.unlink(cls._outputfile)

    @classmethod
    def set_outputfile(cls, fpath, newfile=False):
        """Set the path to a new output file for logging messages."""
        if fpath == cls._outputfile and cls._isopen():
            return
        cls.closefile()
        cls._outputfile = fpath
        cls._fd = None
        if cls._outputfile is not None:
            cls.openfile(newfile=newfile)

    @classmethod
    def set_timestamps(cls, active):
        """Set timestamping on/off for log files."""
        cls._timestamp = bool(active)

    def set_prefix_color(self, color):
        """Set a new color for the prefix text."""
        color = DEFAULT_PREFIX_COLOR if color is None else color
        if WINDOWS:
            self._pref = str
        else:
            self._pref = COL_FUNC[color]

    def set_message_color(self, color):
        """Set a new color for the message text."""
        color = DEFAULT_MSG_COLOR if color is None else color
        if WINDOWS:
            self._msgf = str
        else:
            self._msgf = COL_FUNC[color]

    def __call__(self, *msg, hideprefix=False, popup=False, debug=False,
        error=False, warning=False, **fmt):
        """Display a message with color prefix and multi-line indenting.

        Arguments:
        *msg -- a required string message with optional substitutions

        Keyword arguments:
        prefix -- override default prefix string
        hideprefix -- make prefix invisible but preserve indent
        quiet -- control whether this message is printed (default: quiet mode)
        debug -- specify where this is a debug message
        error -- specify whether this is an error message
        warning -- specify whether this is an warning message
        popup -- display the message with a system popup notification
        **fmt -- remaining kwargs provide formating substitutions
        """
        # Handle a quick exit for non-debug-mode and quiet mode
        prefix = fmt.pop('prefix', self._prefix).strip()
        quiet = fmt.pop('quiet', QUIET_MODE)
        if not (warning or error):
            if quiet or (debug and not DEBUG_MODE):
                return

        # Construct the display prefix
        if debug:
            prefix = 'Debug'
        if warning:
            prefix = 'Warning'
        if error:
            prefix = 'Error'
        if prefix:
            pre = prefix + ': '
        else:
            pre = ''
        pre_len = len(pre)
        if hideprefix:
            pre = ' ' * pre_len

        # Construct the display message
        if len(msg) == 0:
            raise ValueError('message argument is required')
        elif len(msg) == 1:
            msg = str(msg[0])
        else:
            msg, args = msg[0], msg[1:]
            msg = msg.format(*args, **fmt)
        if os.path.sep in msg:
            msg = tilde(msg)

        # Console color print with prefix and indentation
        if error:
            pref = red
            msgf = red
            console = stderr
        elif warning:
            pref = orange
            msgf = orange
            console = stderr
        elif debug:
            pref = dimgray
            msgf = smoke
            console = stdout
        else:
            pref = self._pref
            msgf = self._msgf
            console = stdout

        # Resolve any hanging lines
        if self.__class__._hanging:
            self.newline()

        # Print remaining lines indented and aligned with the first
        lines = msg.split('\n')
        print(pref(pre) + msgf(lines[0]), file=console)
        for line in lines[1:]:
            print(' ' * pre_len + msgf(line), file=console)

        # Timestamped output to the file if it's open
        if self._isopen() and not debug:
            if self._timestamp:
                self._fd.write('[ %s ]  ' % self.timestamp())
            if error:
                self._fd.write('ERROR -> ')
            elif warning:
                self._fd.write('WARNING -> ')
            elif prefix and prefix != self._prefix and not hideprefix:
                self._fd.write(pre)

            # Strip any escape codes (e.g., for color) out of the msg
            msg = re.sub('(\x1b\[\d;\d\dm)|(\x1b\[0m)', '', msg)

            self._fd.write(msg + '\n')
            self._fd.flush()

        # Request a system popup notification
        if popup:
            if self._notifier is None:
                self._notifier = Notifier(prog='Console', echo=False)
            if error:
                self._notifier.notify(msg[7:], 'Console', 'Error')
            elif warning:
                self._notifier.notify(msg[9:], 'Console', 'Warning')
            else:
                self._notifier.notify(msg, 'Console')

    def timestamp(self):
        """Formatted date/time string (ms resolution) for current time."""
        _tfmt = '[%Y-%m-%d+%H:%M+%S.{}]'.format(
                str(time.time()).split('.')[-1][:6].ljust(6, '0'))
        return time.strftime(_tfmt)

    def debug(self, *msg, **fmt):
        """Output in debug mode."""
        fmt.update(debug=True)
        self.__call__(*msg, **fmt)

    def box(self, filled=True, color=None):
        """Draw a Unicode box glyph to the console."""
        self.printf('\u25a1\u25a0'[filled], color=color)

    def hline(self, ch='???', length=80, color='snow'):
        """Print a horizontal rule line."""
        if self.__class__._hanging:
            self.newline()
        self.printf(ch * length + '\n', color=color)

    def newline(self):
        """Insert a newline."""
        self.printf('\n')

    def printf(self, s, color=None):
        """Raw flushed color output to the console."""
        if QUIET_MODE: return

        colf = self._pref if color is None else COL_FUNC[color]
        s = str(s)

        if WINDOWS:
            print(s, end='', flush=True)
        else:
            print(colf(s), end='', flush=True)

        if self._isopen():
            s_nocolor = re.sub('(\x1b\[\d;\d\dm)|(\x1b\[0m)', '', s)
            self._fd.write(s_nocolor)
            self._fd.flush()

        self.__class__._hanging = not s.endswith('\n')


# Convenience functions

Logger = ConsolePrinter()

def log(*args, **kwargs):
    Logger(*args, **kwargs)

def debug(*args, **kwargs):
    kwargs.update(debug=True)
    Logger(*args, **kwargs)

def warn(*args, **kwargs):
    kwargs.update(warning=True)
    Logger(*args, **kwargs)

def error(*args, **kwargs):
    kwargs.update(error=True)
    Logger(*args, **kwargs)

def printf(s, c='green'):
    Logger.printf(s, color=c)

def box(filled=False, c='green'):
    Logger.box(filled=filled, color=c)

def hline(c='snow'):
    Logger.hline(color=c)
