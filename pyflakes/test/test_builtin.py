"""
Tests for detecting redefinition of builtins
"""

from pyflakes import messages as m
from pyflakes.test.harness import TestCase


class TestBuiltins(TestCase):

    def test_redefinition_by_assignment(self):
        self.flakes('''
        range = 10
        ''', m.RedefinedBuiltin)

        self.flakes('''
        def foo(list):
            pass
        ''', m.RedefinedBuiltin)

        self.flakes('''
        __file__ = 10
        ''')

    def test_redefinition_by_overriding(self):
        self.flakes('''
        def min():
            pass
        ''', m.RedefinedBuiltin)

        self.flakes('''
        class max:
            pass
        ''', m.RedefinedBuiltin)

        # Methods do not redefine functions
        self.flakes('''
        class Foo:
            def max():
                pass
        ''')

    def test_redefinition_in_list_comprehension(self):
        self.flakes('''
        a = [max for max in range(0, 10)]
        ''', m.RedefinedBuiltin)

    def test_redefinition_in_loops(self):
        self.flakes('''
        for range in [1,2,3]: print(range)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        while(range):
            range = 0
        ''', m.RedefinedBuiltin)

    def test_redefinition_by_imports(self):
        self.flakes('''
        import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        from package import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        from ..package import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

        self.flakes('''
        from package.max import max
        max(2, 3)
        ''', m.RedefinedBuiltin)

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
        def foo():
            if 'max' not in __builtins__.__dict__:
                def max(a, b):
                    if a >= b:
                        return a
                    else:
                        return b
        ''', m.RedefinedBuiltin)

        self.flakes('''
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
