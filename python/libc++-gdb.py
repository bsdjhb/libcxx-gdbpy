# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# This should be installed as libc++.so.N-gdb.py

import gdb.printing

pythondir = '/home/john/work/git/libc++-gdbpy/python'

if not pythondir in sys.path:
    sys.path.insert(0, pythondir)

import libcxx.printers
gdb.printing.register_pretty_printer(
    gdb.current_objfile(),
    libcxx.printers.build_pretty_printers())

import libcxx.xmethods
libcxx.xmethods.register_libcxx_xmethods(gdb.current_objfile())
