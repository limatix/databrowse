#!/usr/bin/env python
###############################################################################
## Databrowse:  An Extensible Data Management Platform                       ##
## Copyright (C) 2012-2016 Iowa State University Research Foundation, Inc.   ##
## All rights reserved.                                                      ##
##                                                                           ##
## Redistribution and use in source and binary forms, with or without        ##
## modification, are permitted provided that the following conditions are    ##
## met:                                                                      ##
##   1. Redistributions of source code must retain the above copyright       ##
##      notice, this list of conditions and the following disclaimer.        ##
##   2. Redistributions in binary form must reproduce the above copyright    ##
##      notice, this list of conditions and the following disclaimer in the  ##
##      documentation and/or other materials provided with the distribution. ##
##   3. Neither the name of the copyright holder nor the names of its        ##
##      contributors may be used to endorse or promote products derived from ##
##      this software without specific prior written permission.             ##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS       ##
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED ##
## TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A           ##
## PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER ##
## OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,  ##
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,       ##
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR        ##
## PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF    ##
## LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING      ##
## NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS        ##
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.              ##
##                                                                           ##
## This material is based on work supported by the Air Force Research        ##
## Laboratory under Contract #FA8650-10-D-5210, Task Order #023 and          ##
## performed at Iowa State University.                                       ##
##                                                                           ##
## DISTRIBUTION A.  Approved for public release:  distribution unlimited;    ##
## 19 Aug 2016; 88ABW-2016-4051.                                             ##
##                                                                           ##
## This material is based on work supported by NASA under Contract           ##
## NNX16CL31C and performed by Iowa State University as a subcontractor      ##
## to TRI Austin.                                                            ##
##                                                                           ##
## Approved for public release by TRI Austin: distribution unlimited;        ##
## 01 June 2018; by Carl W. Magnuson (NDE Division Director).                ##
###############################################################################
""" requirements.py - Script that determines current system and the required dependencies """

import sys
import os
import time

try: input = raw_input
except NameError: pass


def sanitised_input(prompt, limit_=-1, default_=None, type_=None, min_=None, max_=None, range_=None):
    """
    Generic input prompt
    https://stackoverflow.com/questions/23294658/asking-the-user-for-input-until-they-give-a-valid-response
    :param prompt: Input question to ask user
    :param limit_: Seconds until default_ is return
    :param default_: Default response after limit_
    :param type_: Variable type of the desired response
    :param min_: Minimum value of a valid response
    :param max_: Maximum value of a valid response
    :param range_: Range of valid responses ie. ('a', 'b', 'c')
    :return: User response
    """
    if min_ is not None and max_ is not None and max_ < min_:
        raise ValueError("min_ must be less than or equal to max_.")
    stime = time.time()
    while True:
        try:
            ui = input(prompt)
        except SyntaxError:
            print("Invalid input please try again.")
            continue
        if type_ is not None:
            if type_ != type(ui):
                print("Input type must be {0}.".format(type_.__name__))
                continue
        if max_ is not None and ui > max_:
            print("Input must be less than or equal to {0}.".format(max_))
        elif min_ is not None and ui < min_:
            print("Input must be greater than or equal to {0}.".format(min_))
        elif range_ is not None and ui not in range_:
            if isinstance(range_, type(range)):
                template = "Input must be between {0.start} and {0.stop}."
                print(template.format(range_))
            else:
                template = "Input must be {0}."
                if len(range_) == 1:
                    print(template.format(*range_))
                else:
                    print(template.format(" or ".join((", ".join(map(str, range_[:-1])), str(range_[-1])))))
        elif (time.time() - stime) > limit_ > 0:
            if default_ in range_:
                return default_
            else:
                template = "Default is not a valid response."
                print(template)
        else:
            return ui


def select_requirements_file():
    """
    Return the path to a requirements file based on some os/arch condition.
    """

    answer = sanitised_input("Auto install dependencies with PIP? [y/N]: ", str, limit_=30, default_='N', range_=('y', 'Y', 'n', 'N'))
    if answer not in ['y', 'Y']:
        return 'requirements/null.txt'

    # operating system
    sys_platform = str(sys.platform).lower()
    linux = 'linux' in sys_platform
    windows = 'win32' in sys_platform
    cygwin = 'cygwin' in sys_platform
    solaris = 'sunos' in sys_platform
    macosx = 'darwin' in sys_platform
    posix = 'posix' in os.name.lower()

    # python version
    python_major = sys.version_info[0]
    python_minor = sys.version_info[1]

    if python_major == 2 and python_minor < 7:
        prefix = '26'
    else:
        prefix = ''

    if windows:
        return 'requirements/windows/windows%s.txt' % prefix
    elif macosx:
        return 'requirements/mac/mac%s.txt' % prefix
    elif linux:
        return 'requirements/linux/linux%s.txt' % prefix
    elif cygwin:
        return 'requirements/cygwin/cygwin%s.txt' % prefix
    elif solaris:
        return 'requirements/solaris/solaris%s.txt' % prefix
    elif posix:
        return 'requirements/posix/posix%s.txt' % prefix
    else:
        raise Exception('Unsupported OS/platform')
