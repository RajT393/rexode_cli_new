# Rexode CLI - Universal AI-Powered CLI Assistant

![Rexode CLI Banner](https://raw.githubusercontent.com/RajT393/rexode_cli/main/assets/banner.png) <!-- Placeholder for a banner image -->

Rexode CLI is a powerful, open-source command-line interface assistant designed to streamline your workflow by enabling natural language interaction with your operating system and various tools. From software engineering tasks to data analysis, file automation, and web scraping, Rexode aims to be your intelligent co-pilot, capable of understanding complex multi-step requests and executing them autonomously.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup Steps](#setup-steps)
  - [API Key Configuration](#api-key-configuration)
- [Usage](#usage)
  - [Starting Rexode CLI](#starting-rexode-cli)
  - [LLM Modes](#llm-modes)
  - [Interacting with Rexode](#interacting-with-rexode)
  - [Examples](#examples)
- [Tool System](#tool-system)
  - [Defining Tools in `tools.json`](#defining-tools-in-toolsjson)
  - [Creating Custom Tools](#creating-custom-tools)
- [Agent Collaboration (A2A)](#agent-collaboration-a2a)
- [Knowledge Base](#knowledge-base)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

## Features

Rexode CLI is built with a modular and extensible architecture to provide a wide range of capabilities:

-   **Natural Language Understanding:** Accept complex, multi-step tasks from the user in natural language.
-   **Task Orchestration:** Intelligently split tasks into subtasks, determine required tools, request missing information from the user, and execute all steps end-to-end.
-   **Transparent Execution:** All tasks and execution flow are fully visible to the user in the terminal, providing complete transparency.
-   **Universal Task Handling:** Support for virtually any type of task, including:
    -   Software Engineering (code analysis, project setup, refactoring)
    -   Data Analysis (script execution, data manipulation)
    -   File Automation (file management, directory operations)
    -   Web Browsing & Scraping
    -   Ticket Booking, Scheduling, Messaging (via integrated tools)
    -   And much more, limited only by available tools.
-   **Dynamic Tooling:** Allow the assistant to build or fetch new tools dynamically when not available, and integrate them instantly.
-   **Flexible LLM Backend Selection:**
    -   **Local LLM:** Integrate with local large language models (e.g., via Ollama, Llama.cpp) for privacy and offline capabilities.
    -   **Online LLM:** Connect to cloud-based LLM providers (e.g., OpenAI, Google Gemini, Anthropic) using API keys for powerful, up-to-date models.
    -   **Local Tools Only:** Operate without an LLM, relying on a rule-based intent parser for direct tool execution, ideal for resource-constrained environments or specific automation tasks.
-   **MCP-Style Tool System:** All tools are defined in a single, extensible `tools.json` schema, allowing for easy addition/removal of tools without core code changes. Tools can be local OS commands, Python scripts, web scrapers, API calls, or UI automation scripts.
-   **Agent-to-Agent (A2A) Collaboration:** If a task exceeds Rexode's internal capabilities, it can delegate to external agents, supporting parallel execution of subtasks and merging results for a comprehensive final response.
-   **Knowledge Base (Vector Database):** An optional integrated vector database (ChromaDB) stores and retrieves tool documentation and examples, enabling even smaller LLMs to act "Rexode-aware" and improve tool selection accuracy.
-   **Zero-Shot System Prompt:** Utilizes a single, zero-shot system prompt for all LLMs, explaining available tools, input-output JSON formats, and examples for requesting missing information.
-   **Multi-Turn Conversations:** Supports multi-turn conversations to clarify tasks and gather necessary information.
-   **Concurrent Execution:** Capable of concurrent execution of subtasks where safe and beneficial.
-   **Robustness & Safety:** Designed for bug-free, production-ready operation with graceful error handling, clear logging, and explicit confirmation for destructive actions.
-   **Cross-Platform Compatibility:** Runs seamlessly on Linux, macOS, and Windows.

## Installation

### Prerequisites

Before installing Rexode CLI, ensure you have the following:

-   **Python 3.9+:** [Download Python](https://www.python.org/downloads/)
-   **Git:** [Download Git](https://git-scm.com/downloads)
-   **(Optional for Local LLM):** [Ollama](https://ollama.ai/) installed and a model downloaded (e.g., `ollama run llama2`).
-   **(Optional for Online LLM):** API keys for your chosen LLM provider (e.g., OpenAI, Google Gemini, Anthropic).

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RajT393/rexode_cli.git
    cd rexode_cli
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Some dependencies like `pywin32` (Windows) or `pyaudio` might require additional system libraries. Refer to their respective documentation if you encounter installation issues.*

### API Key Configuration

For Online LLM mode, you need to configure your API keys. Rexode CLI looks for environment variables. You can set them directly in your system or create a `.env` file in the project root.

Create a file named `.env` in the `rexode_cli` project root (where `main.py` is located) and add your keys:

```
# Example for OpenAI
OPENAI_API_KEY="your_openai_api_key_here"

# Example for Google Gemini
GOOGLE_API_KEY="your_google_api_key_here"

# Example for Anthropic
ANTHROPIC_API_KEY="your_anthropic_api_key_here"

# Optional: Specify default local LLM model
LOCAL_LLM_MODEL="llama2"

# Optional: Specify default online LLM provider and model
ONLINE_LLM_PROVIDER="openai" # or "google", "anthropic", "openrouter", "groq"
OPENAI_MODEL="gpt-4-turbo"
GOOGLE_MODEL="gemini-1.5-pro"
ANTHROPIC_MODEL="claude-3-opus-20240229"
```

*Remember to replace `"your_api_key_here"` with your actual keys.*

## Usage

### Starting Rexode CLI

Navigate to the `rexode_cli` directory in your terminal and run:

```bash
python -m src.rexode_cli.main
```

### LLM Modes

Upon startup, Rexode CLI will prompt you to select an LLM mode:

1.  **Local LLM:** Connects to a locally running LLM (e.g., Ollama). Ideal for privacy and offline use.
2.  **Online LLM:** Connects to a cloud-based LLM provider (e.g., OpenAI, Google Gemini). Requires an API key.
3.  **Local Tools Only:** Operates without an LLM, using a rule-based intent parser. Useful for direct automation or resource-constrained environments.

Choose the mode that best suits your needs.

### Interacting with Rexode

Once Rexode is ready, you can type your commands and questions in natural language.

-   **Exit:** Type `exit`, `quit`, or `bye` to gracefully exit the application.
-   **Cancel Current Task:** Press `Esc` to attempt to cancel the current task being processed by Rexode.
-   **Keyboard Shortcuts:**
    -   `Ctrl+Alt+M`: (Planned) Toggle between different operational modes (e.g., "power" mode).
    -   `Ctrl+Alt+S`: Perform screen OCR (Optical Character Recognition) and display the extracted text.

### Examples

Here are some examples of tasks you can give to Rexode (depending on the tools available and LLM capabilities):

-   "Summarize the article at https://example.com/long-article"
-   "Find all Python files in the current directory that contain 'def main' and list their paths."
-   "Create a new directory called 'my_project' and then create a file named 'app.py' inside it with a 'Hello, World!' Python script."
-   "Search the web for the latest news on AI advancements."
-   "Analyze the code in `src/utils.py` and suggest improvements for readability."
-   "Book a flight from New York to London for tomorrow at 3 PM." (Requires a booking tool)
-   "Send a message to John saying 'Meeting at 10 AM'." (Requires a messaging tool)

## Tool System

Rexode's power comes from its flexible tool system. All tools are defined in `tools.json` and can be dynamically loaded.

### Defining Tools in `tools.json`

The `tools.json` file located in the project root defines all available tools. Each tool entry is a JSON object with the following structure:

```json
[
  {
    "name": "tool_name_here",
    "description": "A concise description of what this tool does and when it should be used.",
    "parameters": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Description of the first parameter."
        },
        "param2": {
          "type": "integer",
          "description": "Description of the second parameter."
        }
      },
      "required": ["param1"]
    },
    "examples": [
      {
        "input": "Natural language example of how a user might request this tool.",
        "tool_call": {
          "name": "tool_name_here",
          "parameters": {
            "param1": "example_value",
            "param2": 123
          }
        }
      }
    ]
  }
]
```

-   `name`: (String, required) A unique identifier for the tool.
-   `description`: (String, required) A clear and concise explanation of the tool's functionality. This is crucial for the LLM to understand when to use the tool.
-   `parameters`: (Object, required) A JSON Schema object defining the tool's input parameters. This helps the LLM understand what arguments the tool expects.
-   `examples`: (Array of Objects, optional) Provides natural language examples of user requests and their corresponding tool calls. These examples are used to train the knowledge base and improve LLM's tool selection.

### Creating Custom Tools

You can extend Rexode's capabilities by creating your own tools. Tools can be implemented as Python functions or scripts.

1.  **Implement the Tool Logic:**
    Create a Python file (e.g., `my_custom_tool.py`) in the `src/rexode_cli/tools` directory.
    ```python
    # src/rexode_cli/tools/my_custom_tool.py
    async def perform_my_action(arg1: str, arg2: int) -> str:
        """
        Performs a custom action.
        :param arg1: The first argument.
        :param arg2: The second argument.
        :return: A string indicating the result.
        """
        # Your custom logic here
        result = f"Custom action performed with {arg1} and {arg2}."
        return result
    ```
    *Note: Tools should be asynchronous functions if they involve I/O operations.*

2.  **Define the Tool in `tools.json`:**
    Add an entry to `tools.json` that points to your new tool. The `name` should match the function name, and the `parameters` should match the function's arguments.

    ```json
    {
      "name": "perform_my_action",
      "description": "Performs a custom action with two arguments.",
      "parameters": {
        "type": "object",
        "properties": {
          "arg1": {
            "type": "string",
            "description": "The first argument for the action."
          },
          "arg2": {
            "type": "integer",
            "description": "The second argument for the action."
          }
        },
        "required": ["arg1", "arg2"]
      },
      "examples": [
        {
          "input": "Perform my custom action with 'hello' and 123",
          "tool_call": {
            "name": "perform_my_action",
            "parameters": {
              "arg1": "hello",
              "arg2": 123
            }
          }
        }
      ]
    }
    ```

3.  **Integrate the Tool (Future Enhancement):**
    Currently, tools are loaded from `tools.json` and their execution is simulated. A future enhancement will involve dynamically loading and executing Python functions based on the `tool_name` from `tools.json`. For now, you would manually map the `tool_name` to the actual function in `TaskOrchestrator`'s `_execute_tool` method.

## Agent Collaboration (A2A)

Rexode is designed to be extensible beyond its built-in tools. The Agent-to-Agent (A2A) collaboration framework allows Rexode to delegate complex tasks to external, specialized AI agents. This enables:

-   **Specialized Capabilities:** Leverage agents optimized for specific domains (e.g., a dedicated code generation agent, a financial analysis agent).
-   **Parallel Processing:** Subtasks can be delegated to multiple agents and executed concurrently, speeding up complex workflows.
-   **Scalability:** Easily integrate new agent services as they become available.

*Note: The A2A framework is currently a placeholder. Future development will focus on defining clear interfaces for external agents and implementing robust delegation and result merging mechanisms.*

## Knowledge Base

Rexode utilizes an optional vector database (ChromaDB) to store and retrieve knowledge about its tools and their usage. This knowledge base serves several key purposes:

-   **Enhanced Tool Selection:** By providing relevant tool descriptions and examples as context, even smaller LLMs can make more informed decisions about which tools to use and how to use them.
-   **"Rexode-Awareness":** The LLM gains a deeper understanding of Rexode's capabilities and limitations, leading to more accurate and helpful responses.
-   **Dynamic Learning:** The knowledge base can be updated with new tool information and usage patterns over time, allowing Rexode to continuously improve.

## Development

### Project Structure

```
rexode_cli_new/
├── src/
│   └── rexode_cli/
│       ├── core/                 # Core logic: TaskOrchestrator, ToolManager, KnowledgeBase
│       ├── llm/                  # LLM handling and integration
│       ├── ui/                   # User interface components (banner, indicators)
│       ├── utils/                # Utility functions
│       ├── tools/                # Placeholder for custom Python tools
│       ├── chat_logger.py        # Chat logging functionality
│       ├── mode_manager.py       # Manages operational modes
│       ├── permissions.py        # Handles user permissions
│       ├── subscription.py       # Subscription/trial logic
│       ├── main.py               # Main application entry point
│       └── ...                   # Other core modules
├── config/                     # Configuration files (.env, .rexoderc, plans.json)
├── data/                       # Data files (chat history, downloads, PyWhatKit_DB.txt)
├── prompts/                    # System prompts for LLMs (e.g., system_prompt.txt)
├── tests/                      # Unit and integration tests
├── .gitignore                  # Git ignore file
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── tools.json                  # Centralized tool definitions
```

### Running Tests

*Note: Testing framework and specific tests are under development.*

To run tests (once implemented), you would typically use `pytest`: 

```bash
# From the project root (rexode_cli_new)
pytest tests/
```

## Contributing

We welcome contributions to Rexode CLI! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and ensure they adhere to the project's coding style.
4.  Write tests for your changes.
5.  Submit a pull request with a clear description of your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.