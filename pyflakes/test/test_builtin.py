"""
Tests for detecting redefinition of builtins
"""

from pyflakes import messages as m
from pyflakes.test.harness import TestCase


class TestBuiltins(TestCase):

    def test_redefinition_by_assignment(self):
        self.flakes('''
        range(1)
        range = 10
        ''', m.RedefinedBuiltin)

        self.flakes('''
        x = list()
        def foo(list):
            return list
        ''', m.RedefinedBuiltin)

        self.flakes('''
        print(__file__)
        __file__ = 10
        ''', m.RedefinedBuiltin)

        self.flakes('''
        range = 10
        ''')

        self.flakes('''
        def foo(list):
            return list
        ''')

        self.flakes('''
        __file__ = 10
        ''')

    def test_redefinition_in_class(self):
        self.flakes('''
        class max:
            pass
        ''')

        self.flakes('''
        max(1, 2)
        class max:
            pass
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1, 2)
        class Foo:
            max = 0
        ''', m.RedefinedBuiltin)

    def test_redefinition_in_function(self):
        self.flakes('''
        x = min(1, 2)
        def min():
            pass
        ''', m.RedefinedBuiltin)

        self.flakes('''
        def min():
            pass
        ''')

        self.flakes('''
        max(1, 2)
        class Foo():
            def fun(self):
                def max():
                    pass
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1, 2)
        class Foo():
            def bar(self):
                def foo_bar():
                    max = 1
                    return max
        ''', m.RedefinedBuiltin)

        # Cannot detect decorators
        self.flakes('''
        def decorator(param):
            return param
        
        @decorator(range)
        def range():
            pass
        ''')

        # Acceptable not an error
        self.flakes('''
        range(1)
        def foo(range=range):
            return range(foo)
        ''')

    def test_redefinition_in_lambda(self):
        self.flakes('''
        range(2)
        map(lambda range: range*2, [1, 2, 3, 4])
        ''', m.RedefinedBuiltin)

    def test_redefinition_in_list_comprehension(self):
        self.flakes('''
        max(1, 2)
        a = [max for max in range(0, 10)]
        ''', m.RedefinedBuiltin)

    def test_redefinition_in_loops(self):
        self.flakes('''
        range(0)
        for range in [1, 2, 3]: print(range)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        range(0)
        while(range):
            range = 0
        ''', m.RedefinedBuiltin)

    def test_redefinition_by_imports(self):
        self.flakes('''
        max(1, 2)
        import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1, 2)
        from package import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1, 2)
        from ..package import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1, 2)
        from package.max import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        import max
        max(2, 3)
        ''')

        self.flakes('''
        from package import max
        max(2, 3)
        ''')

        self.flakes('''
        from ..package import max
        max(2, 3)
        ''')

        self.flakes('''
        from package.max import max
        max(2, 3)
        ''')

    def test_ignoring_redefinition_inside_module_guards(self):
        """
        Don't warn when redefinition is at module level
        wrapped inside Try/If block
        """
        self.flakes('''
        try:
            xrange
        except NameError:
            def xrange(start, end):
                for i in range(start, end):
                    yield i
        ''')

        self.flakes('''
        if 'range' not in __builtins__.__dict__:
            def range():
                pass
        ''')

    def test_non_module_level_guards(self):
        """
        Report error if the Try/If guards is not
        at module level
        """

        self.flakes('''
        max(1)
        def foo():
            if 'max' not in __builtins__.__dict__:
                def max(a, b):
                    if a >= b:
                        return a
                    else:
                        return b
        ''', m.RedefinedBuiltin)

        self.flakes('''
        max(1)
        def foo():
            try:
                max
            except NameError:
                def max(a, b):
                    if a >= b:
                        return a
                    else:
                        return b
        ''', m.RedefinedBuiltin)
