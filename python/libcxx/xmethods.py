# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# Xmethods for libc++.

import gdb
import gdb.xmethod
import re

def find_field(type, name):
    for field in type.fields():
        if field.name == name:
            return field
    return None

class StdXMethod(gdb.xmethod.XMethod):
    def __init__(self, name, worker):
        gdb.xmethod.XMethod.__init__(self, name)
        self.worker = worker

class StdListIterator_deref(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type, node_type):
        self.elem_type = elem_type
        self.node_type = node_type

    def get_arg_types(self):
        return None

    def get_result_type(self, obj):
        return self.elem_type

    def __call__(self, obj):
        return obj['__ptr_'].cast(self.node_type)['__value_']

class StdListIteratorMatcher(gdb.xmethod.XMethodMatcher):
    def __init__(self):
        gdb.xmethod.XMethodMatcher.__init__(self, "list::iterator")
        self.methods = [StdXMethod("operator*", StdListIterator_deref)]

    def match(self, class_type, method_name):
        if not re.match('^std::__1::__list_(const)?iterator<.*>', class_type.tag):
            return None
        ptr_field = find_field(class_type, '__ptr_')
        if not ptr_field:
            return None
        link_type = ptr_field.type.strip_typedefs().target()
        node_type_name = str(link_type).replace('__list_node_base', '__list_node', 1)
        try:
            node_type = gdb.lookup_type(node_type_name).pointer()
        except:
            return None
        for method in self.methods:
            if method.name == method_name:
                if method.enabled:
                    return method.worker(class_type.template_argument(0), node_type)
        return None

class StdUniquePtr_get(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def get_arg_types(self):
        return None

    def get_result_type(self, obj):
        return self.elem_type.pointer()

    def __call__(self, obj):
        return obj['__ptr_']['__value_']

class StdUniquePtr_deref(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def get_arg_types(self):
        return None

    def get_result_type(self, obj):
        return self.elem_type

    def __call__(self, obj):
        return obj['__ptr_']['__value_'].dereference()

class StdUniquePtrMatcher(gdb.xmethod.XMethodMatcher):
    def __init__(self):
        gdb.xmethod.XMethodMatcher.__init__(self, "unique_ptr")
        self.methods = [StdXMethod("get", StdUniquePtr_get),
                        StdXMethod("operator->", StdUniquePtr_get),
                        StdXMethod("operator*", StdUniquePtr_deref)]

    def match(self, class_type, method_name):
        if not re.match('^std::__1::unique_ptr<.*>', class_type.tag):
            return None
        for method in self.methods:
            if method.name == method_name:
                if method.enabled:
                    return method.worker(class_type.template_argument(0))
        return None

class StdVector_subscript(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def get_arg_types(self):
        return gdb.lookup_type('size_t')

    def get_result_type(self, obj):
        return self.elem_type

    def __call__(self, obj, index):
        begin = obj['__begin_']
        return (begin + int(index)).dereference()

class StdVectorMatcher(gdb.xmethod.XMethodMatcher):
    def __init__(self):
        gdb.xmethod.XMethodMatcher.__init__(self, "vector")
        self.methods = [StdXMethod("operator[]", StdVector_subscript)]

    def match(self, class_type, method_name):
        if not re.match('^std::__1::vector<.*>', class_type.tag):
            return None
        for method in self.methods:
            if method.name == method_name:
                if method.enabled:
                    return method.worker(class_type.template_argument(0))
        return None

def register_libcxx_xmethods(objfile):
    gdb.xmethod.register_xmethod_matcher(objfile, StdListIteratorMatcher())
    gdb.xmethod.register_xmethod_matcher(objfile, StdUniquePtrMatcher())
    gdb.xmethod.register_xmethod_matcher(objfile, StdVectorMatcher())
