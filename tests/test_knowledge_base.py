import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rexode_cli.core.knowledge_base import KnowledgeBase

class TestKnowledgeBase(unittest.TestCase):

    @patch('chromadb.PersistentClient')
    def setUp(self, mock_persistent_client):
        """Set up a test environment before each test."""
        self.mock_collection = Mock()
        mock_persistent_client.return_value.get_or_create_collection.return_value = self.mock_collection
        self.knowledge_base = KnowledgeBase()

    def test_add_tool_documentation(self):
        """Test that tool documentation is added to the knowledge base correctly."""
        tool_name = "test_tool"
        description = "A test tool."
        examples = [
            {"input": "use test tool", "tool_call": {}},
            {"input": "run test tool", "tool_call": {}}
        ]

        self.knowledge_base.add_tool_documentation(tool_name, description, examples)

        self.mock_collection.add.assert_called_once()
        call_args, call_kwargs = self.mock_collection.add.call_args
        self.assertEqual(len(call_kwargs['documents']), 3)
        self.assertEqual(len(call_kwargs['metadatas']), 3)
        self.assertEqual(len(call_kwargs['ids']), 3)

    def test_query_knowledge_base(self):
        """Test that the knowledge base can be queried correctly."""
        query_text = "how to use test tool"
        self.mock_collection.query.return_value = {
            'documents': [['doc1', 'doc2']],
            'metadatas': [[{'type': 'tool_description'}, {'type': 'tool_example'}]],
            'distances': [[0.1, 0.2]]
        }

        documents, metadatas, distances = self.knowledge_base.query_knowledge_base(query_text)

        self.mock_collection.query.assert_called_once_with(
            query_texts=[query_text],
            n_results=5,
            include=['documents', 'metadatas', 'distances']
        )
        self.assertEqual(len(documents), 2)
        self.assertEqual(len(metadatas), 2)
        self.assertEqual(len(distances), 2)

if __name__ == '__main__':
    unittest.main()