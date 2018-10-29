# GDB Helpers for LLVM's libc++

This repository contains helpers to aid debugging of programs using
libc++ under GDB.  GDB helpers are written in python and come in two
flavors.  Pretty printers provide custom 'print' output for libc++
objects.  Xmethods provide python implementations of libc++ object
methods so that a developer can use these operators in expressions in
GDB.

For example, the pretty printer for `std::string<>` changes the output
from:

```
(gdb) p str
$1 = {<std::__1::__basic_string_common<true>> = {<No data fields>}, 
  static __short_mask = 1, static __long_mask = 1, 
  __r_ = {<std::__1::__compressed_pair_elem<std::__1::basic_string<char, std::__1::char_traits<char>, std::__1::allocator<char> >::__rep, 0, false>> = {__value_ = {{
          __l = {__cap_ = 122511465736202, __size_ = 0, __data_ = 0x0}, __s = {{
              __size_ = 10 '\n', __lx = 10 '\n'}, 
            __data_ = "hello", '\000' <repeats 17 times>}, __r = {__words = {
              122511465736202, 0, 
              0}}}}}, <std::__1::__compressed_pair_elem<std::__1::allocator<char>, 1, true>> = {<std::__1::allocator<char>> = {<No data fields>}, <No data fields>}, <No data fields>}, static npos = 18446744073709551615}
```

to:

```
(gdb) p str
$1 = "hello"
```

The std::vector<>::operator[] xmethod permits a developer to use array
indices directly:

```
(gdb) p numbers
$1 = std::vector of length 20 = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 
  15, 16, 17, 18, 19}
(gdb) p numbers[10]
$2 = 10
```

## Pretty Printers

This table lists the pretty printers implemented to date.

| Class | Notes |
| ----- | ----- |
| std::string |
| std::unique_ptr<T> |
| std::vector<T> | T = bool not supported |

## Xmethods

This table lists the xmethods implemented to date.

| Class | Method | Notes |
| ----- | ------ | ----- |
| std::unique_ptr<T> | get |
| std::unique_ptr<T> | operator-> | Not tested with T[] |
| std::unique_ptr<T> | operator* | Not tested with T[] |
| std::vector<T> | operator[] |

## Installation / Using

This is a bit hacky currently.  GDB's auto-loading support looks for
python scripts named *library*-gdb.py.  That means that the top-level
script `libc++-gdb.py` needs to be installed in the same path as your
existing libc++ library.  For example, if libc++ is installed as
`/usr/lib/libc++.so.1` as on FreeBSD, then `libc++-gdb.py` needs to be
copied to `/usr/lib/libc++-gdb.py`.  The `pythondir` in the installed
script should point to a directory holding the contents of the
`python` subdirectory.  The checked-in version hardcodes the path to
my git checkout path which is probably not what you want.
