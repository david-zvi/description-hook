import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from hook_runner import COMMANDS, POWERSHELLS, run


class PythonFallbackTest(unittest.TestCase):
    """Every hooks.json command runs `python3 script || python script`. If python3 reads the input
    and then fails, python must still get the full input."""

    def setUp(self):
        fake_bin = tempfile.TemporaryDirectory()
        self.addCleanup(fake_bin.cleanup)
        self.python3_input_file = os.path.join(fake_bin.name, "python3_input.json")

        broken_python3 = os.path.join(fake_bin.name, "python3")
        with open(broken_python3, "w") as f:
            f.write(f"""#!/bin/sh
# Broken python3: save all the input it was given, print nothing, and fail.
cat > "{self.python3_input_file}"
exit 1
""")
        os.chmod(broken_python3, 0o755)
        working_python = os.path.join(fake_bin.name, "python")
        os.symlink(sys.executable, working_python)

        # The shell runs the first `python3` / `python` it finds in PATH's folders, so fake_bin goes first.
        self.path_where_python3_is_broken = fake_bin.name + os.pathsep + os.environ["PATH"]

    def test_python_receives_input_after_python3_used_it_up(self):
        for event_name in COMMANDS:
            with self.subTest(event=event_name):
                event = {"hook_event_name": event_name, "tool_name": "Bash", "tool_input": {"command": "ls"}}

                python_output = run(event, "hooks.json", path=self.path_where_python3_is_broken)

                self.assertTrue(os.path.exists(self.python3_input_file), "the broken python3 never ran")
                with open(self.python3_input_file) as f:
                    python3_input = json.load(f)
                os.remove(self.python3_input_file)  # so the next event starts without this file
                self.assertEqual(python3_input, event, "the broken python3 didn't read the whole input")
                self.assertIsNotNone(python_output, "the fallback python printed nothing")


class PowerShellPythonFallbackTest(unittest.TestCase):
    """The PowerShell hook runs `py -3` if the py launcher exists, otherwise `python`."""

    def test_python_runs_when_py_is_missing(self):
        python_folder = os.path.dirname(sys.executable)
        if not POWERSHELLS:
            self.skipTest("no PowerShell installed")
        if not shutil.which("python", path=python_folder):
            self.skipTest(f"no `python` in {python_folder}")
        if shutil.which("py", path=python_folder):
            self.skipTest(f"`py` is in {python_folder}, so it can't be hidden")

        event = {"hook_event_name": "PreToolUse", "tool_name": "PowerShell", "tool_input": {"command": "ls"}}
        for powershell in POWERSHELLS:
            with self.subTest(powershell=powershell):
                # With only Python's own folder on PATH, `py` isn't found and the hook falls back to `python`.
                out = run(event, "hooks.json", path=python_folder, powershell=powershell)
                self.assertEqual(out and out["permissionDecision"], "deny")


class PythonMissingTest(unittest.TestCase):
    """When no Python runs, each hook fails with a note telling the user how to get unstuck."""

    def check_hook_fails_with_note(self, tool_name, powershell=None):
        event = {"hook_event_name": "PreToolUse", "tool_name": tool_name, "tool_input": {"command": "ls"}}
        with tempfile.TemporaryDirectory() as empty_folder:
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                run(event, "hooks.json", path=empty_folder, powershell=powershell)
        self.assertIn("disable the plugin with /plugin", failure.exception.stderr)

    def test_bash_hook(self):
        self.check_hook_fails_with_note("Bash")

    def test_powershell_hook(self):
        if not POWERSHELLS:
            self.skipTest("no PowerShell installed")
        for powershell in POWERSHELLS:
            with self.subTest(powershell=powershell):
                self.check_hook_fails_with_note("PowerShell", powershell)


if __name__ == "__main__":
    unittest.main()
