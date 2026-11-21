import ast
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SixCompatibilityTests(unittest.TestCase):
    def test_no_ansible_six_imports(self):
        for directory in ('library', 'action_plugins', 'module_utils'):
            for path in (ROOT / directory).rglob('*.py'):
                tree = ast.parse(path.read_bytes(), filename=str(path))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        self.assertFalse((node.module or '').startswith('ansible.module_utils.six'), str(path))
                    elif isinstance(node, ast.Import):
                        self.assertFalse(any(alias.name.startswith('ansible.module_utils.six') for alias in node.names), str(path))

    def test_comparisons_keep_dictionary_behavior(self):
        path = ROOT / 'module_utils/network/f5/compare.py'
        spec = importlib.util.spec_from_file_location('f5_compare', path)
        compare = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(compare)
        self.assertIsNone(compare.compare_dictionary({'a': 1}, {'a': 1}))
        self.assertIsNotNone(compare.compare_dictionary({'a': 1}, {'a': 2}))
        self.assertIsNone(compare.compare_complex_list([{'a': 1}], [{'a': 1}]))
        self.assertIsNotNone(compare.compare_complex_list([{'a': 1}], [{'a': 2}]))


if __name__ == '__main__':
    unittest.main()
