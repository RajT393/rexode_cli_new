import sys
import os
import asyncio
from unittest.mock import Mock # Import Mock (for testing AIOperator directly)

# Add the current directory to sys.path if not already present
# This is to ensure modules within 'src' are discoverable when run from project root
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

from .cli import CLI
from .ai_operator import AIOperator
from .llm_handler import LLMHandler # Import LLMHandler

def main():
    # Initialize LLMHandler once
    llm_handler = LLMHandler()

    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        task = " ".join(sys.argv[2:])
        if not task:
            print("Usage: python -m src.rexode_cli.main auto <task_description>")
            sys.exit(1)

        # For 'auto' mode, we need a real LLM for AIOperator
        # Prompt user for LLM choice for AIOperator
        print("Configuring LLM for AI Operator (auto mode):")
        print("  1. Local LLM (e.g., Ollama, Llama.cpp)")
        print("  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key")
        
        while True:
            llm_choice = input("Enter your choice (1 or 2): ").strip()
            if llm_choice in ["1", "2"]:
                break
            print("Invalid choice. Please enter 1 or 2.")

        llm_instance = None
        if llm_choice == "1":
            model_name = input("Enter local model name (e.g., llama2, mistral): ").strip()
            llm_instance = llm_handler.initialize_llm(llm_type="local", model_name=model_name)
        elif llm_choice == "2":
            provider = input("Enter online LLM provider (e.g., openai, google, anthropic): ").strip().lower()
            model_name = input("Enter model name (e.g., gpt-4, gemini-1.5-pro): ").strip()
            llm_instance = llm_handler.initialize_llm(llm_type="online", provider=provider, model_name=model_name)
        
        if llm_instance is None:
            print("Failed to initialize LLM for AI Operator. Exiting.")
            sys.exit(1)

        operator = AIOperator(model=llm_instance) # Pass the initialized LLM
        asyncio.run(operator.run(task))
    else:
        # Interactive CLI mode
        cli = CLI()
        asyncio.run(cli.run())

if __name__ == "__main__":
    main()
