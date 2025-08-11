import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List, Dict, Any

class KnowledgeBase:
    def __init__(self, persist_directory: str = "knowledge_base_db"):
        self.persist_directory = os.path.join(os.path.dirname(__file__), "..", "..", "..", persist_directory)
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Using a default embedding function. For production, consider more robust ones.
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        self.collection = self.client.get_or_create_collection(
            name="rexode_tools_knowledge",
            embedding_function=self.embedding_function
        )

    def add_tool_documentation(self, tool_name: str, description: str, examples: List[Dict[str, str]]):
        """Adds tool documentation and examples to the knowledge base."""
        documents = [description]
        metadatas = [{"type": "tool_description", "tool_name": tool_name}]
        ids = [f"{tool_name}_description"]

        for i, example in enumerate(examples):
            documents.append(f"Example for {tool_name}: {example.get('input')}")
            metadatas.append({"type": "tool_example", "tool_name": tool_name, "example_id": i})
            ids.append(f"{tool_name}_example_{i}")
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added documentation for tool: {tool_name}")

    def query_knowledge_base(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Queries the knowledge base for relevant information."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        return results['documents'][0], results['metadatas'][0], results['distances'][0]

# Example usage (for testing purposes)
if __name__ == "__main__":
    kb = KnowledgeBase()

    # Add some dummy tool data
    kb.add_tool_documentation(
        "example_tool_1",
        "This tool performs a specific action with two parameters.",
        [
            {"input": "Use example tool 1 with value A and 123", "tool_call": {}},
            {"input": "Perform action using tool 1 with X and 45", "tool_call": {}}
        ]
    )
    kb.add_tool_documentation(
        "example_tool_2",
        "This tool searches for information based on a query.",
        [
            {"input": "Search for 'AI assistant'", "tool_call": {}},
            {"input": "Find data about machine learning", "tool_call": {}}
        ]
    )

    # Query the knowledge base
    print("\nQuerying for 'how to use tool 1':")
    documents, metadatas, distances = kb.query_knowledge_base("how to use tool 1")
    for doc, meta, dist in zip(documents, metadatas, distances):
        print(f"  Doc: {doc}, Meta: {meta}, Distance: {dist:.2f}")

    print("\nQuerying for 'find information':")
    documents, metadatas, distances = kb.query_knowledge_base("find information")
    for doc, meta, dist in zip(documents, metadatas, distances):
        print(f"  Doc: {doc}, Meta: {meta}, Distance: {dist:.2f}")
