import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "neo4j_mcp_wrapper.py"
SPEC = importlib.util.spec_from_file_location("neo4j_mcp_wrapper", SCRIPT)
wrapper = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = wrapper
SPEC.loader.exec_module(wrapper)


class Neo4jWrapperTests(unittest.TestCase):
    def test_missing_password_fails_closed(self):
        with patch.object(wrapper, "_load_user_env", return_value=""):
            with self.assertRaises(SystemExit):
                wrapper.main()

    def test_start_forces_read_write_mode(self):
        with patch.object(wrapper, "_load_user_env", return_value="test-only"), patch(
            "runpy.run_module"
        ) as run_module, patch.dict(os.environ, {}, clear=True):
            wrapper.main()
            self.assertEqual(os.environ["NEO4J_READ_ONLY"], "false")
            self.assertEqual(os.environ["NEO4J_PASSWORD"], "test-only")
            run_module.assert_called_once_with("neo4j_mcp_server", run_name="__main__")


if __name__ == "__main__":
    unittest.main()
