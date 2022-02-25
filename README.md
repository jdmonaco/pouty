# pouty

The `pouty` package is a collection of tools for enabling fast and flexible messaging and logging. The main `pouty.ConsolePrinter` class makes it easy to print colorful info/warning/error/debug messages with automatic prefixes, indenting, and format-string interpolation of arguments. Message output can be directed to logfiles, system/desktop notifications, or a menubar widget (see below).

## Dependencies

*Note: This section will be updated as the packaging and dependencies are fixed.*

My [`roto`](https://github.com/jdmonaco/roto) package is a required dependency. There are also two optional dependencies, if you want to use them:

1. [tonsky/AnyBar](https://github.com/tonsky/AnyBar): The `pouty.anybar` module communicates color updates to the AnyBar menubar widget in macOS, which you can coordinate with state changes in your program, etc.
1. [julianXX/terminal-notifier](https://github.com/julienXX/terminal-notifier): Setting `popup=True` on output calls will also attempt to emit a desktop notification. If `terminal-notifier` is on your path, then it will be called instead of the default, which is to use an AppleScript (`osascript`) notification.

## Todo

- [ ] Fix dependencies for other packages of mine (e.g., remove or add as submodules)
- [ ] Update the `setup.py` to ensure correct installation, etc.
- [ ] Improve function and class APIs to enhance usabililty and convenience
- [ ] Code style and formatting consistency (e.g., `flake8` validation)
