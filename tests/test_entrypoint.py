from unittest import TestCase
from rambo import EntryPoint
from abc import ABC


class TestEntryPoint(TestCase):

    def test_is_abc(self):
        self.assertTrue(issubclass(EntryPoint, ABC))

    def test_abstract_methods(self):
        abstract_method_names = ['run']

        for abstract_method_name in abstract_method_names:
            self.assertTrue(hasattr(EntryPoint, abstract_method_name))
            self.assertIn(abstract_method_name, EntryPoint.__dict__['__abstractmethods__'])

    def test_entry_point_args(self):
        self.assertTrue(hasattr(EntryPoint, 'entry_point_args'))

    def test_static_methods(self):
        exp_static_method_names = [
            'load_app_env',
        ]

        static_method_names = [name for name, value in EntryPoint.__dict__.items() if type(value) == staticmethod]

        for static_method_name in static_method_names:
            self.assertIn(static_method_name, exp_static_method_names)

        for exp_static_method_name in exp_static_method_names:
            self.assertIn(exp_static_method_name, static_method_names)

    def test_class_methods(self):
        exp_class_method_names = [
            'new',
            'is_entry_point',
            '_validate_class_name',
            'name'
        ]

        class_method_names = [name for name, value in EntryPoint.__dict__.items() if type(value) == classmethod]

        for class_method_name in class_method_names:
            self.assertIn(class_method_name, exp_class_method_names)

        for exp_class_method_name in exp_class_method_names:
            self.assertIn(exp_class_method_name, exp_class_method_names)
