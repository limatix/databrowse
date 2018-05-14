import sys
import os


def select_requirements_file():
    """
    Print the path to a requirements file based on some os/arch condition.
    """

    # operating system
    sys_platform = str(sys.platform).lower()
    linux = 'linux' in sys_platform
    windows = 'win32' in sys_platform
    cygwin = 'cygwin' in sys_platform
    solaris = 'sunos' in sys_platform
    macosx = 'darwin' in sys_platform
    posix = 'posix' in os.name.lower()

    if windows:
        return 'requirements/windows.txt'
    elif macosx:
        return 'requirements/mac.txt'
    elif linux:
        return 'requirements/linux.txt'
    elif cygwin:
        return 'requirements/cygwin.txt'
    else:
        raise Exception('Unsupported OS/platform')
