### Code credits to:
### https://stackoverflow.com/users/2030627/fred271828
### https://stackoverflow.com/questions/1167617/in-python-how-do-i-indicate-im-overriding-a-method

import re
import inspect

def overrides(method):
    stack = inspect.stack()
    base_classes = re.search(r'class.+\((.+)\)\s*\:', stack[2][4][0]).group(1)
    base_classes = [s.strip() for s in base_classes.split(',')]
    if not base_classes:
        raise ValueError('overrides decorator: unable to determine base class')
    derived_class_locals = stack[2][0].f_locals
    for i, base_class in enumerate(base_classes):
        if '.' not in base_class:
            base_classes[i] = derived_class_locals[base_class]
        else:
            components = base_class.split('.')
            obj = derived_class_locals[components[0]]
            for c in components[1:]:
                assert(inspect.ismodule(obj) or inspect.isclass(obj))
                obj = getattr(obj, c)
            base_classes[i] = obj
    if not any(hasattr(cls, method.__name__) for cls in base_classes):
        raise ValueError('override failed on ' + str(method))
    return method
