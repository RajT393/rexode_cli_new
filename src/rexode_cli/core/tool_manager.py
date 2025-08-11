import json
import os
from typing import Dict, Any
from .knowledge_base import KnowledgeBase # Import KnowledgeBase

class ToolManager:
    def __init__(self, tools_json_path: str):
        self.tools_json_path = tools_json_path
        self.tools = self._load_tools()
        self.knowledge_base = KnowledgeBase() # Initialize KnowledgeBase
        self._populate_knowledge_base() # Populate KB after loading tools

    def _load_tools(self) -> Dict[str, Any]:
        """Loads tools from the tools.json file."""
        try:
            with open(self.tools_json_path, 'r') as f:
                tools_data = json.load(f)
            loaded_tools = {}
            for tool_def in tools_data:
                name = tool_def.get("name")
                if name:
                    loaded_tools[name] = tool_def
            return loaded_tools
        except FileNotFoundError:
            print(f"Error: tools.json not found at {self.tools_json_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {self.tools_json_path}")
            return {}

    def _populate_knowledge_base(self):
        """Populates the knowledge base with tool documentation and examples."""
        for tool_name, tool_def in self.tools.items():
            description = tool_def.get("description", "")
            examples = tool_def.get("examples", [])
            self.knowledge_base.add_tool_documentation(tool_name, description, examples)

    def get_tool_definition(self, tool_name: str) -> Dict[str, Any] | None:
        """Returns the definition of a specific tool."""
        return self.tools.get(tool_name)

    def get_all_tool_names(self) -> list[str]:
        """Returns a list of all available tool names."""
        return list(self.tools.keys())

    def get_all_tool_descriptions(self) -> Dict[str, str]:
        """Returns a dictionary of tool names to their descriptions."""
        return {name: tool_def.get("description", "No description provided.") for name, tool_def in self.tools.items()}

# Example usage (for testing purposes)
if __name__ == "__main__":
    # Assuming tools.json is in the project root for this example
    tool_manager = ToolManager(os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools.json"))
    print("All tool names:", tool_manager.get_all_tool_names())
    print("Tool 'example_tool_1' definition:", tool_manager.get_tool_definition("example_tool_1"))
    print("All tool descriptions:", tool_manager.get_all_tool_descriptions())

    # You can also query the knowledge base directly from the tool manager
    print("\nQuerying knowledge base via ToolManager for 'how to use tool 1':")
    documents, metadatas, distances = tool_manager.knowledge_base.query_knowledge_base("how to use tool 1")
    for doc, meta, dist in zip(documents, metadatas, distances):
        print(f"  Doc: {doc}, Meta: {meta}, Distance: {dist:.2f}")