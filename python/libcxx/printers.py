# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# Pretty-printers for libc++.

import gdb
import gdb.printing

class StdUniquePtrPrinter:
    """Print a std::unique_ptr"""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        v = self.val['__ptr_']['__value_']
        return "std::unique_ptr<%s> = %s" % (v.type.target(), v)

class StdVectorPrinter:
    """Print a std::vector"""

    class __iterator:
        def __init__(self, begin, end):
            self.current = begin
            self.end = end
            self.count = 0

        def __iter__(self):
            return self

        def next(self):
            if self.current == self.end:
                raise StopIteration
            else:
                item = self.current.dereference()
                count = self.count
                self.current = self.current + 1
                self.count = self.count + 1
                return ('[%d]' % count, item)

    def __init__(self, val):
        self.val = val

    def children(self):
        return self.__iterator(self.val['__begin_'], self.val['__end_'])

    def display_hint(self):
        return 'array'

    def to_string(self):
        begin = self.val['__begin_']
        end = self.val['__end_']
        return "std::vector of length %d" % int(end - begin)

class StdStringPrinter:
    """Print a std::string"""

    def __init__(self, val):
        self.val = val

    def display_hint(self):
        return 'string'

    def to_string(self):
        r_first = self.val['__r_']['__value_']
        is_long = (r_first['__s']['__size_'] & self.val['__short_mask']) != 0
        if is_long:
            pointer = r_first['__l']['__data_']
            size = r_first['__l']['__size_']
        else:
            pointer = r_first['__s']['__data_']
            size = r_first['__s']['__size_']
            if int(self.val['__short_mask']) == 1:
                size = size >> 1;
        return pointer.string(length = size)

def build_pretty_printers():
    pp = gdb.printing.RegexpCollectionPrettyPrinter("libc++")
    pp.add_printer('unique_ptr', '^std::__1::unique_ptr<.*>$',
                   StdUniquePtrPrinter)
    pp.add_printer('vector', '^std::__1::vector<.*>$', StdVectorPrinter)
    pp.add_printer('string', '^std::__1::basic_string<.*>$', StdStringPrinter)
    return pp
