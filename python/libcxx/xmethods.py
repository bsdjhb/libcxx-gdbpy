# This file is distributed under the University of Illinois Open Source
# License. See LICENSE.TXT for details.
#
# Xmethods for libc++.

import gdb
import gdb.xmethod
import re

class StdXMethod(gdb.xmethod.XMethod):
    def __init__(self, name, worker):
        gdb.xmethod.XMethod.__init__(self, name)
        self.worker = worker

class StdUniquePtr_get(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def get_arg_types(self):
        return None

    def get_result_type(self, obj):
        return self.elem_type

    def __call__(self, obj):
        return obj['__ptr_']['__value_']

class StdUniquePtr_get(gdb.xmethod.XMethodWorker):
    def __init__(self, elem_type):
        self.elem_type = elem_type

    def get_arg_types(self):
        return None

    def get_result_type(self, obj):
        return self.elem_type

    def __call__(self, obj):
        return obj['__ptr_']['__value_']

class StdUniquePtrMatcher(gdb.xmethod.XMethodMatcher):
    def __init__(self):
        gdb.xmethod.XMethodMatcher.__init__(self, "unique_ptr")
        self.methods = [StdXMethod("get", StdUniquePtr_get),
                        StdXMethod("operator->", StdUniquePtr_get),
                        StdXMethod("operator*", StdUniquePtr_get)]

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
    gdb.xmethod.register_xmethod_matcher(objfile, StdUniquePtrMatcher())
    gdb.xmethod.register_xmethod_matcher(objfile, StdVectorMatcher())
