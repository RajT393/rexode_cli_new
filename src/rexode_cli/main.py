import sys
import os

# Add the current directory to sys.path if not already present
# This is to ensure modules within 'src' are discoverable when run from project root
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

import asyncio
from unittest.mock import Mock # Import Mock

from .cli import CLI
from .ai_operator import AIOperator

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        task = " ".join(sys.argv[2:])
        if not task:
            print("Usage: python -m src.rexode_cli.main auto <task_description>")
            sys.exit(1)

        # Create a mock model for AIOperator
        mock_model = Mock()
        # Define the behavior of the query method for the mock model
        # This is a simplified example; in a real scenario, this would be a real LLM call
        mock_model.query.side_effect = lambda prompt: "CLI_COMMAND" # Default classification

        operator = AIOperator(model=mock_model) # Pass the mock model
        asyncio.run(operator.run(task))
    else:
        cli = CLI()
        asyncio.run(cli.run())

if __name__ == "__main__":
    main()
