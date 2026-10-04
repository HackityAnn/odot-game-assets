import ast
import unittest

from tools.checks import Scripts, worker_violations


class GuardrailTests(unittest.TestCase):
    def test_missing_blender_exit_flag_is_rejected(self):
        self.assertTrue(worker_violations(ast.parse("subprocess.run([blender, '-b', '--python', script])")))
        self.assertFalse(worker_violations(ast.parse("subprocess.run([blender, '-b', '--python-exit-code', '1', '--python', script])")))

    def test_incorrect_exit_code_and_unsupported_save_api_are_rejected(self):
        self.assertTrue(worker_violations(ast.parse("subprocess.run([blender, '--python-exit-code', '0', '--python', script])")))
        self.assertTrue(worker_violations(ast.parse("bpy.data.libraries.write(path, data)")))

    def test_script_extraction_ignores_external_and_json_scripts(self):
        parser=Scripts()
        parser.feed('<script src="vendor.js"></script><script type="application/json">{"asset": 1}</script><script>const value=1;</script>')
        self.assertEqual(parser.scripts,['const value=1;'])
