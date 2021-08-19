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

def dequeBlockSize(value_type):
    if value_type.sizeof < 256:
        return 4096 / value_type.sizeof
    else:
        return 16

class StdDequePrinter:
    """Print a std::deque"""

    class __iterator(IteratorBase):
        def __init__(self, block_size, begin, end, start, size):
            self.block_size = block_size
            self.begin = begin
            self.end = end
            self.start = start
            self.count = size

        def __iter__(self):
            return self

        def __next__(self):
            if self.count == 0:
                raise StopIteration
            item_ptr = self.begin.dereference() + self.start
            item = item_ptr.dereference()
            self.start = self.start + 1
            if self.start == self.block_size:
                self.begin = self.begin + 1
                self.start = 0
            self.count = self.count - 1
            return ("", item)

    def __init__(self, val, name="deque"):
        self.val = val
        self.name = name

        # __block_size is generally optimized out and not available here
        value_type = self.val.type.template_argument(0)
        self.block_size = dequeBlockSize(value_type)

    def children(self):
        map_val = self.val['__map_']
        return self.__iterator(self.block_size, map_val['__begin_'],
                               map_val['__end_'], self.val['__start_'],
                               self.val['__size_']['__value_'])

    def display_hint(self):
        return 'array'

    def to_string(self):
        i = self.val['__size_']['__value_']
        return "std::%s with %d element%s" % (self.name, i,
                                              "" if i == 1 else "s")

class StdDequeIteratorPrinter:
    """Print a std::deque::iterator"""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        item = self.val['__ptr_'].dereference()
        return str(item)

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
        return self.__iterator(self.val['__end_'], self.node_type)

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

class StdUnorderedMapPrinter:
    """Print a std::unordered_map"""

    class __iterator(IteratorBase):
        def __init__(self, begin, node_type):
            self.current = begin
            self.node_type = node_type
            self.state = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.current == 0:
                raise StopIteration
            else:
                node = self.current.cast(self.node_type)
                if self.state == 0:
                    name = 'key'
                    item = node['__value_']['__cc']['first']
                    self.state = 1
                else:
                    name = 'value'
                    item = node['__value_']['__cc']['second']
                    self.state = 0
                    self.current = self.current['__next_']
                return (name, item)

    def __init__(self, val):
        self.val = val
        next_type = val['__table_']['__p1_']['__value_'].type
        self.node_type = next_type.template_argument(0)

    def children(self):
        return self.__iterator(self.val['__table_']['__p1_']['__value_']['__next_'],
                               self.node_type)

    def display_hint(self):
        return 'map'

    def to_string(self):
        i = self.val['__table_']['__p2_']['__value_']
        return "std::unordered_map with %d element%s" % (i, "" if i == 1 else "s")

class StdUnorderedMapIteratorPrinter:
    """Print a std::unordered_map::iterator"""

    def __init__(self, val):
        self.val = val
        iter_type = self.val.type.template_argument(0)
        self.node_type = iter_type.template_argument(0)

    def to_string(self):
        node = self.val['__i_']['__node_'].cast(self.node_type)
        if node == 0:
            return "end()"
        key = node['__value_']['__cc']['first']
        value = node['__value_']['__cc']['second']
        return "[%s] = %s" % (str(key), str(value))

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

class StdStackPrinter:
    """Print a std::stack"""

    def __init__(self, val):
        self.child = StdDequePrinter(val['c'], "stack")

    def children(self):
        return self.child.children()

    def display_hint(self):
        return self.child.display_hint()

    def to_string(self):
        return self.child.to_string()

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
    pp.add_printer('deque', '^std::__1::deque<.*>$', StdDequePrinter)
    pp.add_printer('deque::iterator', '^std::__1::__deque_iterator<.*>$',
                   StdDequeIteratorPrinter)
    pp.add_printer('forward_list', '^std::__1::forward_list<.*>$', StdForwardListPrinter)
    pp.add_printer('forward_list::iterator', '^std::__1::__forward_list_(const_)?iterator<.*>$',
                   StdForwardListIteratorPrinter)
    pp.add_printer('list', '^std::__1::list<.*>$', StdListPrinter)
    pp.add_printer('list::iterator', '^std::__1::__list_(const_)?iterator<.*>$',
                   StdListIteratorPrinter)
    pp.add_printer('stack', '^std::__1::stack<.*>$', StdStackPrinter)
    pp.add_printer('unique_ptr', '^std::__1::unique_ptr<.*>$',
                   StdUniquePtrPrinter)
    pp.add_printer('unordered_map', '^std::__1::unordered_map<.*>$',
                   StdUnorderedMapPrinter)
    pp.add_printer('unordered_map::iterator', '^std::__1::__hash_map_(const_)?iterator<.*>$',
                   StdUnorderedMapIteratorPrinter)
    pp.add_printer('vector', '^std::__1::vector<.*>$', StdVectorPrinter)
    pp.add_printer('string', '^std::__1::basic_string<.*>$', StdStringPrinter)
    return pp
