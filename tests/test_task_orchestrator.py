import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rexode_cli.core.task_orchestrator import TaskOrchestrator
from src.rexode_cli.core.tool_manager import ToolManager
from src.rexode_cli.llm_handler import LLMHandler
from src.rexode_cli.core.config import Config

class TestTaskOrchestrator(unittest.TestCase):

    def setUp(self):
        """Set up a test environment before each test."""
        self.config = Config()
        self.tool_manager = Mock(spec=ToolManager)
        self.llm_handler = Mock(spec=LLMHandler)
        self.task_orchestrator = TaskOrchestrator(
            tool_manager=self.tool_manager,
            llm_handler=self.llm_handler
        )
        self.task_orchestrator.is_cancelled = False

    def test_process_with_rules_parameter_extraction(self):
        """Test that the rule-based processor can extract parameters from user input."""
        user_input = "list_files path=."
        self.tool_manager.tools = [
            {
                "category": "OS & File Management",
                "tools": [
                    {
                        "name": "list_files",
                        "description": "Lists all files and directories in a given path.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "path": {
                                    "type": "string",
                                    "description": "The path of the directory to list."
                                }
                            },
                            "required": ["path"]
                        },
                        "examples": []
                    }
                ]
            }
        ]
        self.tool_manager.get_tool.return_value = lambda path: f"files in {path}"

        result = self.task_orchestrator.process_with_rules(user_input)
        
        self.assertEqual(result, "files in .")

    def test_process_with_rules_complex_parameter_extraction(self):
        """Test that the rule-based processor can extract parameters from complex user input."""
        user_input = "write_file file_path=/home/user/test.txt content='Hello World'"
        self.tool_manager.tools = [
            {
                "category": "OS & File Management",
                "tools": [
                    {
                        "name": "write_file",
                        "description": "Writes content to a file.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to."
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file."
                                }
                            },
                            "required": ["file_path", "content"]
                        },
                        "examples": []
                    }
                ]
            }
        ]
        self.tool_manager.get_tool.return_value = lambda file_path, content: f"wrote to {file_path} with content {content}"

        result = self.task_orchestrator.process_with_rules(user_input)
        
        self.assertEqual(result, "wrote to /home/user/test.txt with content Hello World")

    def test_process_with_rules_quoted_parameter_extraction(self):
        """Test that the rule-based processor can extract quoted parameters from user input."""
        user_input = "write_file file_path='/home/user/test.txt' content='Hello World'"
        self.tool_manager.tools = [
            {
                "category": "OS & File Management",
                "tools": [
                    {
                        "name": "write_file",
                        "description": "Writes content to a file.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to."
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file."
                                }
                            },
                            "required": ["file_path", "content"]
                        },
                        "examples": []
                    }
                ]
            }
        ]
        self.tool_manager.get_tool.return_value = lambda file_path, content: f"wrote to {file_path} with content {content}"

        result = self.task_orchestrator.process_with_rules(user_input)
        
        self.assertEqual(result, "wrote to /home/user/test.txt with content Hello World")

    def test_process_with_rules_parameter_with_spaces_extraction(self):
        """Test that the rule-based processor can extract parameters with spaces from user input."""
        user_input = "write_file file_path='/home/user/test.txt' content='Hello World'"
        self.tool_manager.tools = [
            {
                "category": "OS & File Management",
                "tools": [
                    {
                        "name": "write_file",
                        "description": "Writes content to a file.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path of the file to write to."
                                },
                                "content": {
                                    "type": "string",
                                    "description": "The content to write to the file."
                                }
                            },
                            "required": ["file_path", "content"]
                        },
                        "examples": []
                    }
                ]
            }
        ]
        self.tool_manager.get_tool.return_value = lambda file_path, content: f"wrote to {file_path} with content {content}"

        result = self.task_orchestrator.process_with_rules(user_input)
        
        self.assertEqual(result, "wrote to /home/user/test.txt with content Hello World")

    def test_process_with_rules_tool_not_found(self):
        """Test that the rule-based processor handles cases where no tool is found."""
        user_input = "do something that doesn't exist"
        self.tool_manager.tools = []
        result = self.task_orchestrator.process_with_rules(user_input)
        self.assertEqual(result, "No tool detected.")

if __name__ == '__main__':
    unittest.main()