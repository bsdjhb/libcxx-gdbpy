# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# Pretty-printers for libc++.

import gdb
import gdb.printing

class IteratorBase:
    """Provide python 2.x compat for iterators"""

    def next(self):
        return self.__next__()
    
class StdForwardListPrinter:
    """Print a std::forward_list"""

    class __iterator(IteratorBase):
        def __init__(self, head):
            self.current = head
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.current == 0:
                raise StopIteration
            else:
                item = self.current['__value_']
                count = self.count
                self.current = self.current['__next_']
                self.count = self.count + 1
                return ('[%d]' % count, item)

    def __init__(self, val):
        self.val = val

    def children(self):
        return self.__iterator(self.val['__before_begin_']['__value_']['__next_'])

    def to_string(self):
        if self.val['__before_begin_']['__value_']['__next_'] == 0:
            return "empty std::forward_list"
        return "std::forward_list"

class StdForwardListIteratorPrinter:
    """Print a std::forward_list::iterator"""

    def __init__(self, val):
        self.val = val
        link_type = self.val['__ptr_'].type.strip_typedefs().target()
        self.node_type = link_type.template_argument(0)

    def to_string(self):
        node = self.val['__ptr_'].cast(self.node_type)
        item = node['__value_']
        return str(item)

class StdListPrinter:
    """Print a std::list"""

    class __iterator(IteratorBase):
        def __init__(self, head, node_type):
            self.current = head['__next_']
            self.end = head.address
            self.node_type = node_type
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.current == self.end:
                raise StopIteration
            else:
                node = self.current.cast(self.node_type)
                item = node['__value_']
                count = self.count
                self.current = self.current['__next_']
                self.count = self.count + 1
                return ('[%d]' % count, item)

    def __init__(self, val):
        self.val = val
        self.node_type = gdb.lookup_type(self.val.type.name + '::__node_pointer')

    def size(self):
        return self.val['__size_alloc_']['__value_']

    def children(self):
        head = self.val['__end_']
        return self.__iterator(self.val['__end_'], self.nodetype)

    def to_string(self):
        if self.size() == 0:
            return "empty std::list"
        return "std::list"

class StdListIteratorPrinter:
    """Print a std::list::iterator"""

    def __init__(self, val):
        self.val = val
        link_type = self.val['__ptr_'].type.strip_typedefs().target()
        node_type_name = str(link_type).replace('__list_node_base', '__list_node', 1)
        self.node_type = gdb.lookup_type(node_type_name).pointer()

    def to_string(self):
        node = self.val['__ptr_'].cast(self.node_type)
        item = node['__value_']
        return str(item)

class StdUniquePtrPrinter:
    """Print a std::unique_ptr"""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        v = self.val['__ptr_']['__value_']
        return "std::unique_ptr<%s> = %s" % (v.type.target(), v)

class StdVectorPrinter:
    """Print a std::vector"""

    class __iterator(IteratorBase):
        def __init__(self, begin, end):
            self.current = begin
            self.end = end
            self.count = 0

        def __iter__(self):
            return self

        def __next__(self):
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
    pp.add_printer('forward_list', '^std::__1::forward_list<.*>$', StdForwardListPrinter)
    pp.add_printer('forward_list::iterator', '^std::__1::__forward_list_(const)?iterator<.*>$',
                   StdForwardListIteratorPrinter)
    pp.add_printer('list', '^std::__1::list<.*>$', StdListPrinter)
    pp.add_printer('list::iterator', '^std::__1::__list_(const)?iterator<.*>$',
                   StdListIteratorPrinter)
    pp.add_printer('unique_ptr', '^std::__1::unique_ptr<.*>$',
                   StdUniquePtrPrinter)
    pp.add_printer('vector', '^std::__1::vector<.*>$', StdVectorPrinter)
    pp.add_printer('string', '^std::__1::basic_string<.*>$', StdStringPrinter)
    return pp
