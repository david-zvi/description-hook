import json
import os
import sys
import tempfile
import unittest

from hook_runner import COMMANDS, run


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

                python_output = run(event, path=self.path_where_python3_is_broken)

                self.assertTrue(os.path.exists(self.python3_input_file), "the broken python3 never ran")
                with open(self.python3_input_file) as f:
                    python3_input = json.load(f)
                os.remove(self.python3_input_file)  # so the next event starts without this file
                self.assertEqual(python3_input, event, "the broken python3 didn't read the whole input")
                self.assertIsNotNone(python_output, "the fallback python printed nothing")


if __name__ == "__main__":
    unittest.main()
