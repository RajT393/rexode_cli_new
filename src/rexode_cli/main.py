import sys
import getpass
import asyncio
from rich.console import Console
from rich.panel import Panel

# ============== RELATIVE IMPORTS ==============
try:
    from .ai_operator import AIOperator
    from .utils.logger import get_logger
    logger = get_logger("rexode_cli")
except ImportError:
    # fallback if running directly
    from src.rexode_cli.ai_operator import AIOperator
    try:
        from src.rexode_cli.utils.logger import get_logger
        logger = get_logger("rexode_cli")
    except Exception:
        class _DummyLogger:
            def info(self, x): print(x)
            def debug(self, x): print(x)
            def warning(self, x): print(x)
            def error(self, x): print(x)
        logger = _DummyLogger()

console = Console()

# ============== UI ELEMENTS ==============
BANNER = r"""
██████╗ ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔════╝
██████╔╝█████╗   ╚███╔╝ ██║   ██║██║  ██║█████╗
██╔══██╗██╔══╝    ███╗  ██║   ██║██║  ██║██╔══╝
██║  ██║███████╗██╔╝ ██╗╚██████╔╝██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝
REXODE CLI - Your all-in-one AI assistant 🧠⚡
"""
TIP = "💡 Tip: Press Ctrl+Alt+M to switch modes | Ctrl+Alt+S for screen OCR"
MENU = """\
Select an LLM Mode:
  1. Local LLM (e.g., Ollama, Llama.cpp)
  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key
  3. Local Tools Only (No LLM - Rule-based/agentic tools)
"""

# ============== OPERATOR FACTORY ==============
def _make_operator(mode_config: dict):
    try:
        operator = AIOperator(mode_config)
    except TypeError:
        operator = AIOperator()

    if hasattr(operator, "set_mode") and callable(operator.set_mode):
        try: operator.set_mode(mode_config)
        except Exception as e: logger.warning(f"[AIOperator.set_mode warning] {e}")

    if hasattr(operator, "configure") and callable(operator.configure):
        try: operator.configure(mode_config)
        except Exception as e: logger.warning(f"[AIOperator.configure warning] {e}")

    return operator

# ============== SAFE RUNNER ==============
async def _maybe_await(func, *args, **kwargs):
    result = func(*args, **kwargs)
    if asyncio.iscoroutine(result):
        return await result
    return result

# ============== INTERACTIVE LOOP ==============
async def _interactive_loop(prompt_prefix: str, operator: AIOperator, mode_config: dict):
    console.print("[green]Rexode is ready![/green]\n")
    while True:
        try:
            user_input = input(f"You ({prompt_prefix})> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                console.print("[red]👋 Goodbye from Rexode.[/red]")
                break
            if not user_input:
                continue

            result = await _maybe_await(operator.run, user_input, context=mode_config)

            if result is not None:
                console.print(
                    Panel(
                        str(result).strip(),
                        title="Rexode",
                        border_style="cyan",
                        expand=True,
                        padding=(1, 2)
                    )
                )
        except (KeyboardInterrupt, EOFError):
            console.print("\n[red]👋 Goodbye from Rexode.[/red]")
            break
        except Exception as e:
            logger.error(f"[Runtime Error] {e}")

# ============== MODE CONFIG COLLECTORS ==============
def _collect_local_llm_config() -> dict:
    console.print("[bold cyan]📍 Local LLM mode selected.[/bold cyan]")
    provider = input("Enter local LLM provider (e.g., ollama, llama.cpp, vllm): ").strip()
    model = input("Enter model name (e.g., llama3.1, qwen2.5): ").strip()
    host = input("Enter local server host (default http://127.0.0.1:11434): ").strip() or "http://127.0.0.1:11434"
    return {"mode": "local_llm","provider": provider,"model": model,"host": host,"allow_gui": True,"allow_web": True,"allow_n8n": True}

def _collect_online_llm_config() -> dict:
    console.print("[bold cyan]🌐 Online LLM mode selected.[/bold cyan]")
    provider = input("Enter online LLM provider (e.g., openai, google, anthropic, openrouter): ").strip()
    model = input("Enter model name (e.g., gpt-4o, gemini-2.5-flash, claude-3.5): ").strip()
    key_label = {"openai":"OPENAI","google":"GOOGLE","anthropic":"ANTHROPIC","openrouter":"OPENROUTER"}.get(provider.lower(), provider.upper())
    api_key = getpass.getpass(f"Enter {key_label} API key (hidden): ").strip()
    return {"mode":"online_llm","provider":provider,"model":model,"api_key":api_key,"allow_gui":True,"allow_web":True,"allow_n8n":True}

def _collect_local_tools_config() -> dict:
    console.print("[bold cyan]🛠️  Local Tools Only mode selected.[/bold cyan]")
    return {"mode":"local_tools_only","allow_gui":True,"allow_web":True,"allow_n8n":True}

# ============== ENTRYPOINT ==============
def main():
    console.print(BANNER, style="bold magenta")
    console.print(TIP, style="yellow")
    console.print("\nRexode is ready!\n", style="green")
    console.print(MENU, style="cyan")

    choice = input("Enter your choice (1, 2, or 3): ").strip()
    if choice == "1": mode_config = _collect_local_llm_config()
    elif choice == "2": mode_config = _collect_online_llm_config()
    elif choice == "3": mode_config = _collect_local_tools_config()
    else:
        console.print("[red]❌ Invalid choice. Exiting.[/red]")
        sys.exit(1)

    operator = _make_operator(mode_config)
    asyncio.run(_interactive_loop(mode_config["mode"], operator, mode_config))

if __name__ == "__main__":
    main()


'''# src/rexode_cli/main.py

import sys
import getpass

# ============== RELATIVE IMPORTS ==============
# Makes sure it works with `python -m src.rexode_cli.main`
from .ai_operator import AIOperator
try:
    from .utils.logger import get_logger
    logger = get_logger("rexode_cli")
except Exception:
    class _DummyLogger:
        def info(self, x): print(x)
        def debug(self, x): print(x)
        def warning(self, x): print(x)
        def error(self, x): print(x)
    logger = _DummyLogger()

# ============== UI ELEMENTS ==============
BANNER = r"""
██████╗ ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔════╝
██████╔╝█████╗   ╚███╔╝ ██║   ██║██║  ██║█████╗
██╔══██╗██╔══╝    ███╗  ██║   ██║██║  ██║██╔══╝
██║  ██║███████╗██╔╝ ██╗╚██████╔╝██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝
REXODE CLI - Your all-in-one AI assistant 🧠⚡
"""

TIP = "💡 Tip: Press Ctrl+Alt+M to switch modes | Ctrl+Alt+S for screen OCR"

MENU = """\
Select an LLM Mode:
  1. Local LLM (e.g., Ollama, Llama.cpp)
  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key
  3. Local Tools Only (No LLM - Rule-based/agentic tools)
"""

# ============== OPERATOR FACTORY ==============
def _make_operator(mode_config: dict):
    """Safely instantiate AIOperator with mode_config."""
    try:
        operator = AIOperator(mode_config)
    except TypeError:
        operator = AIOperator()

    if hasattr(operator, "set_mode") and callable(operator.set_mode):
        try:
            operator.set_mode(mode_config)
        except Exception as e:
            logger.warning(f"[AIOperator.set_mode warning] {e}")

    if hasattr(operator, "configure") and callable(operator.configure):
        try:
            operator.configure(mode_config)
        except Exception as e:
            logger.warning(f"[AIOperator.configure warning] {e}")

    return operator

# ============== INTERACTIVE LOOP ==============
def _interactive_loop(prompt_prefix: str, operator: AIOperator, mode_config: dict):
    logger.info("Rexode is ready!\n")
    while True:
        try:
            user_input = input(f"You ({prompt_prefix})> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye from Rexode.")
                break
            if not user_input:
                continue

            try:
                result = operator.run(user_input, context=mode_config)
            except TypeError:
                result = operator.run(user_input)

            if result is not None:
                print("\n╭─ Rexode " + "─" * 60 + "╮")
                print(f"│ {str(result).strip()}")
                print("╰" + "─" * 70 + "╯")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye from Rexode.")
            break
        except Exception as e:
            logger.error(f"[Runtime Error] {e}")

# ============== MODE CONFIG COLLECTORS ==============
def _collect_local_llm_config() -> dict:
    print("📍 Local LLM mode selected.")
    provider = input("Enter local LLM provider (e.g., ollama, llama.cpp, vllm): ").strip()
    model = input("Enter model name (e.g., llama3.1, qwen2.5): ").strip()
    host = input("Enter local server host (default http://127.0.0.1:11434): ").strip() or "http://127.0.0.1:11434"

    return {
        "mode": "local_llm",
        "provider": provider,
        "model": model,
        "host": host,
        "allow_gui": True,
        "allow_web": True,
        "allow_n8n": True,
    }

def _collect_online_llm_config() -> dict:
    print("🌐 Online LLM mode selected.")
    provider = input("Enter online LLM provider (e.g., openai, google, anthropic, openrouter): ").strip()
    model = input("Enter model name (e.g., gpt-4o, gemini-2.5-flash, claude-3.5): ").strip()

    key_label = {
        "openai": "OPENAI",
        "google": "GOOGLE",
        "anthropic": "ANTHROPIC",
        "openrouter": "OPENROUTER",
    }.get(provider.lower(), provider.upper())

    api_key = getpass.getpass(f"Enter {key_label} API key (hidden): ").strip()

    return {
        "mode": "online_llm",
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "allow_gui": True,
        "allow_web": True,
        "allow_n8n": True,
    }

def _collect_local_tools_config() -> dict:
    print("🛠️  Local Tools Only mode selected.")
    return {
        "mode": "local_tools_only",
        "allow_gui": True,
        "allow_web": True,
        "allow_n8n": True,
    }

# ============== ENTRYPOINT ==============
def main():
    print(BANNER)
    print(TIP)
    print("\nRexode is ready!\n")
    print(MENU)

    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        mode_config = _collect_local_llm_config()
    elif choice == "2":
        mode_config = _collect_online_llm_config()
    elif choice == "3":
        mode_config = _collect_local_tools_config()
    else:
        print("❌ Invalid choice. Exiting.")
        sys.exit(1)

    operator = _make_operator(mode_config)
    _interactive_loop(mode_config["mode"], operator, mode_config)

if __name__ == "__main__":
    main()
'''

'''# src/rexode_cli/main.py

import sys
import getpass

# Use RELATIVE imports so `python -m src.rexode_cli.main` works
from .ai_operator import AIOperator
# If you have a logger util, keep this import. If not, it will fall back to prints.
try:
    from .utils.logger import get_logger
    logger = get_logger("rexode_cli")
except Exception:
    class _DummyLogger:
        def info(self, x): print(x)
        def debug(self, x): print(x)
        def warning(self, x): print(x)
        def error(self, x): print(x)
    logger = _DummyLogger()

BANNER = r"""
██████╗ ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔════╝
██████╔╝█████╗   ╚███╔╝ ██║   ██║██║  ██║█████╗
██╔══██╗██╔══╝    ███╗  ██║   ██║██║  ██║██╔══╝
██║  ██║███████╗██╔╝ ██╗╚██████╔╝██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝
REXODE CLI - Your all-in-one AI assistant 🧠⚡
"""

TIP = "💡 Tip: Press Ctrl+Alt+M to switch modes | Ctrl+Alt+S for screen OCR"

MENU = """\
Select an LLM Mode:
  1. Local LLM (e.g., Ollama, Llama.cpp)
  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key
  3. Local Tools Only (No LLM - Rule-based/agentic tools)
"""

def _make_operator(mode_config: dict):
    """
    Instantiate AIOperator while staying compatible with your current ai_operator.py.
    If your class __init__ accepts config -> use it; otherwise fall back to no-arg init.
    Also call set_mode/configure if present.
    """
    try:
        operator = AIOperator(mode_config)  # preferred (new) signature
    except TypeError:
        operator = AIOperator()  # backward compatibility

    # optional hooks if your operator exposes them
    if hasattr(operator, "set_mode") and callable(operator.set_mode):
        try:
            operator.set_mode(mode_config)
        except Exception as e:
            logger.warning(f"[AIOperator.set_mode warning] {e}")

    if hasattr(operator, "configure") and callable(operator.configure):
        try:
            operator.configure(mode_config)
        except Exception as e:
            logger.warning(f"[AIOperator.configure warning] {e}")

    return operator

def _interactive_loop(prompt_prefix: str, operator: AIOperator, mode_config: dict):
    """
    Unified REPL for all three modes. Sends every line to AIOperator.run()
    and prints the result if any.
    """
    logger.info("Rexode is ready!\n")
    while True:
        try:
            user_input = input(f"You ({prompt_prefix})> ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("Goodbye from Rexode.")
                break
            if not user_input:
                continue

            # Call run(). If your run() accepts context, pass it; otherwise fallback.
            try:
                result = operator.run(user_input, context=mode_config)
            except TypeError:
                result = operator.run(user_input)

            if result is not None:
                # Uniform, simple output envelope
                print("\n╭─ Rexode " + "─" * 100 + "╮")
                print(f"│ {str(result).strip()}")
                print("╰" + "─" * 118 + "╯")
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye from Rexode.")
            break
        except Exception as e:
            logger.error(f"[Runtime Error] {e}")

def _collect_local_llm_config() -> dict:
    print("Local LLM mode selected.")
    provider = input("Enter local LLM provider (e.g., ollama, llama.cpp, vllm): ").strip()
    model = input("Enter model name (e.g., llama3.1, qwen2.5): ").strip()
    # Optional host/port if your local server needs it
    host = input("Enter local server host (default http://127.0.0.1:11434): ").strip() or "http://127.0.0.1:11434"

    return {
        "mode": "local_llm",
        "provider": provider,
        "model": model,
        "host": host,
        # strategy flags you can read in ai_operator to decide GUI/CLI/web/n8n usage
        "allow_gui": True,
        "allow_web": True,
        "allow_n8n": True,
    }

def _collect_online_llm_config() -> dict:
    print("Online LLM mode selected.")
    provider = input("Enter online LLM provider (e.g., openai, google, anthropic, openrouter): ").strip()
    model = input("Enter model name (e.g., gpt-4o, gemini-2.5-flash, claude-3.5): ").strip()

    # Read API key label based on provider for nice UX
    key_label = {
        "openai": "OPENAI",
        "google": "GOOGLE",
        "anthropic": "ANTHROPIC",
        "openrouter": "OPENROUTER",
    }.get(provider.lower(), provider.upper())

    api_key = getpass.getpass(f"Enter {key_label} API key (will be hidden): ").strip()

    return {
        "mode": "online_llm",
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "allow_gui": True,
        "allow_web": True,
        "allow_n8n": True,
    }

def _collect_local_tools_config() -> dict:
    print("Local Tools Only mode selected.")
    # You can extend this with toggles if needed
    return {
        "mode": "local_tools_only",
        "allow_gui": True,   # let it operate PC via GUI (pyautogui/sikuli/etc.)
        "allow_web": True,   # let it use local browser automation (Selenium/Playwright)
        "allow_n8n": True,   # let it call n8n via REST locally
    }

def main():
    print(BANNER)
    print(TIP)
    print("\nRexode is ready!\n")
    print(MENU)

    choice = input("Enter your choice (1, 2, or 3): ").strip()

    if choice == "1":
        mode_config = _collect_local_llm_config()
        operator = _make_operator(mode_config)
        _interactive_loop(mode_config["mode"], operator, mode_config)

    elif choice == "2":
        mode_config = _collect_online_llm_config()
        operator = _make_operator(mode_config)
        _interactive_loop(mode_config["mode"], operator, mode_config)

    elif choice == "3":
        mode_config = _collect_local_tools_config()
        operator = _make_operator(mode_config)
        _interactive_loop(mode_config["mode"], operator, mode_config)

    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
'''
import sys
from rexode_cli.ai_operator import AIOperator
from rexode_cli.utils.logger import get_logger

logger = get_logger("rexode_cli")

def main():
    logger.info("🚀 Starting Rexode CLI...")

    # Initialize AI Operator
    operator = AIOperator()

    # If arguments are passed, treat them as a single prompt
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        logger.debug(f"CLI received input: {user_input}")
        operator.run(user_input)
    else:
        # Interactive mode
        logger.info("Entering interactive mode. Type 'exit' to quit.")
        while True:
            try:
                user_input = input("rexode> ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    logger.info("Exiting Rexode CLI.")
                    break
                if not user_input:
                    continue
                operator.run(user_input)
            except (KeyboardInterrupt, EOFError):
                logger.info("Exiting Rexode CLI (keyboard exit).")
                break

if __name__ == "__main__":
    main()
'''

'''import sys
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
'''