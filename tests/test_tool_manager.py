import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rexode_cli.core.tool_manager import ToolManager
from src.rexode_cli.core.config import Config

class TestToolManager(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.config = Config()
        # Create a dummy tools.json for testing
        self.test_tools_path = os.path.join(os.path.dirname(__file__), 'test_tools.json')
        self.config.TOOLS_JSON_PATH = self.test_tools_path
        with open(self.test_tools_path, 'w') as f:
            f.write("""[
                {
                    "category": "Test Tools",
                    "tools": [
                        {
                            "name": "test_tool_1",
                            "description": "A test tool.",
                            "parameters": {},
                            "examples": []
                        }
                    ]
                }
            ]""")

    def tearDown(self):
        """Clean up the test environment after each test."""
        os.remove(self.test_tools_path)

    def test_load_tools(self):
        """Test that the ToolManager loads tools correctly from a JSON file."""
        tool_manager = ToolManager(self.config)
        self.assertIsNotNone(tool_manager.tools)
        self.assertEqual(len(tool_manager.tools), 1)
        self.assertEqual(tool_manager.tools[0]['category'], 'Test Tools')

    def test_get_tool_not_found(self):
        """Test that get_tool returns None for a non-existent tool."""
        tool_manager = ToolManager(self.config)
        tool = tool_manager.get_tool('non_existent_tool')
        self.assertIsNone(tool)

if __name__ == '__main__':
    unittest.main()