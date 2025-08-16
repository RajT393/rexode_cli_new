import json
import os
import importlib.util

from .config import Config

class ToolManager:
    def __init__(self, config: Config):
        self.tools = self.load_tools(config.TOOLS_JSON_PATH)
        self.tool_functions = self.load_tool_functions()

    def load_tools(self, tools_json_path):
        with open(tools_json_path, 'r') as f:
            return json.load(f)

    def load_tool_functions(self):
        tool_functions = {}
        tools_dir = os.path.join(os.path.dirname(__file__), "..", "tools")
        for filename in os.listdir(tools_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = os.path.join(tools_dir, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for tool_category in self.tools:
                    for tool in tool_category['tools']:
                        if hasattr(module, tool['name']):
                            tool_functions[tool['name']] = getattr(module, tool['name'])
        return tool_functions

    def get_tool(self, tool_name):
        return self.tool_functions.get(tool_name)
