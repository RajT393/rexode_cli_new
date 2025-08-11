import os
import sys
import signal
import threading
import time
import asyncio
from pynput import keyboard
from datetime import datetime
from .banner import print_banner
from .mode_manager import load_mode, save_mode, get_mode_config
from .voice_listener import get_voice_input
from .permissions import ask_permission, save_permissions, load_permissions
from .chat_logger import ensure_log_folder, get_today_log_path, append_chat
from .shortcut_handler import listen_for_shortcuts
from .popup_manager import show_confirmation
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from .subscription import (
    load_subscription,
    is_subscription_active,
    enforce_subscription,
    activate_trial
)
from .core.tool_manager import ToolManager
from .core.task_orchestrator import TaskOrchestrator
from .llm_handler import LLMHandler # Import LLMHandler
# Removed: from langchain.agents import initialize_agent, Tool
# Removed: from langchain.memory import ConversationBufferMemory
# from tools import tools # Replaced by ToolManager
from rich.console import Console
from rich.panel import Panel
from .inline_activity_indicator import InlineActivityIndicator
from langchain.callbacks.base import BaseCallbackHandler
from .task_ui import TaskUI

# Globals
exit_confirmed = False
chat_mode = "text"
permissions = {}
chat_history_path = ""
subscription_data = {}
mode_config = {}
llm = None
model_name = ""
cancel_event = threading.Event()
should_exit = False # New global flag for graceful exit

def on_press(key):
    try:
        if key == keyboard.Key.esc:
            print("ESC key pressed!") # Debug print
            cancel_event.set()
            return False # Stop listener
    except AttributeError:
        pass # Handle special keys that don't have a .char attribute

class CustomAgentCallbackHandler(BaseCallbackHandler):
    def __init__(self, indicator: InlineActivityIndicator):
        self.indicator = indicator

    def on_tool_start(self, tool: dict, input_str: str, **kwargs) -> None:
        self.indicator.start(f"Using tool: {tool.name}")

    def on_tool_end(self, output: str, **kwargs) -> None:
        self.indicator.start("Agent thinking...") # Revert to thinking after tool ends

    def on_agent_action(self, action: dict, **kwargs) -> None:
        self.indicator.start(f"Agent thought: {action.log.strip()}")

    def on_agent_finish(self, finish: dict, **kwargs) -> None:
        self.indicator.stop()

def graceful_exit(sig, frame):
    global exit_confirmed, should_exit
    if exit_confirmed:
        print("\nExiting Rexode CLI.")
        should_exit = True # Set flag instead of sys.exit(0)
    else:
        print("\nPress Ctrl+C again within 10 seconds to confirm exit.")
        exit_confirmed = True
        def reset_flag():
            global exit_confirmed
            exit_confirmed = False
        threading.Timer(10.0, reset_flag).start()

async def main():
    global permissions, chat_history_path, subscription_data, mode_config, chat_mode, llm, model_name, should_exit

    console = Console()
    signal.signal(signal.SIGINT, graceful_exit)

    # Start keyboard listener for ESC key
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    print_banner()
    ensure_log_folder()
    chat_history_path = get_today_log_path()
    subscription_data = load_subscription()

    if not is_subscription_active():
        enforce_subscription()

    activate_trial()

    os.makedirs("config", exist_ok=True)
    save_mode("power")
    load_mode()
    mode_config = get_mode_config()

    permissions = load_permissions()

    threading.Thread(target=listen_for_shortcuts, daemon=True).start()

    console.print("Rexode is ready!", style="bold green")

    # Initialize LLMHandler and InlineActivityIndicator before mode selection
    llm_handler = LLMHandler()
    agent_indicator = InlineActivityIndicator(console, "Rexode is thinking...")

    # --- Mode Selection ---
    selected_mode = None
    while selected_mode not in ["1", "2", "3"]:
        console.print("\nSelect an LLM Mode:", style="bold blue")
        console.print("  1. Local LLM (e.g., Ollama, Llama.cpp)", style="blue")
        console.print("  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key", style="blue")
        console.print("  3. Local Tools Only (No LLM - Rule-based intent parser)", style="blue")
        selected_mode = console.input("[bold green]Enter your choice (1, 2, or 3): [/bold green]").strip()

        if selected_mode == "1":
            console.print("Local LLM mode selected.", style="bold green")
            model_name = console.input("[bold green]Enter local model name (e.g., llama2, mistral): [/bold green]").strip()
            llm = llm_handler.get_llm(llm_type="local", model_name=model_name)
            if not llm:
                console.print("Failed to initialize Local LLM. Exiting.", style="bold red")
                return
        elif selected_mode == "2":
            console.print("Online LLM mode selected.", style="bold green")
            provider = console.input("[bold green]Enter online LLM provider (e.g., openai, google, anthropic): [/bold green]").strip().lower()
            model_name = console.input("[bold green]Enter model name (e.g., gpt-4, gemini-1.5-pro): [/bold green]").strip()
            api_key = console.input("[bold green]Enter API key (will be hidden): [/bold green]", password=True).strip() # Use password=True for hidden input
            llm = llm_handler.get_llm(llm_type="online", provider=provider, model_name=model_name, api_key=api_key)
            if not llm:
                console.print("Failed to initialize Online LLM. Exiting.", style="bold red")
                return
        elif selected_mode == "3":
            console.print("Local Tools Only mode selected.", style="bold green")
            model_name = "local_tools_only" # Placeholder
            llm = None # No LLM in this mode
        else:
            console.print("Invalid choice. Please enter 1, 2, or 3.", style="bold red")

    # Initialize ToolManager
    tools_json_path = os.path.join(os.path.dirname(__file__), "..", "..", "tools.json")
    tool_manager = ToolManager(tools_json_path)

    # Initialize TaskOrchestrator based on selected mode
    orchestrator = TaskOrchestrator(tool_manager, llm=llm, llm_mode=model_name)

    # --- LangChain Agent Initialization (for LLM modes) ---
    # Removed agent initialization from here. TaskOrchestrator now handles it.

    while not should_exit:
        try:
            response_content = "" # Initialize response_content here
            if chat_mode == "voice":
                user_input = get_voice_input()
                if not user_input:
                    continue
                console.print(Panel(user_input, title="You", title_align="left", border_style="blue"))
            else:
                user_input = console.input(f"You ({model_name})> ").strip()

            if user_input.lower() in ["exit", "quit", "bye"]:
                console.print("Goodbye from Rexode.", style="bold red")
                break

            append_chat(f"You: {user_input}", f"")
            
            # Start indicator before invoking the orchestrator
            agent_indicator.start()
            
            # Use the TaskOrchestrator to process the task, which now internally handles LLM agent if applicable
            response_content = await orchestrator.process_task(user_input)

            # Ensure indicator is stopped and event is cleared
            agent_indicator.stop()
            console.print()
            cancel_event.clear() # Clear the event for the next input

            console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
            console.print(f"[dim]Mode: {model_name}[/dim]", justify="right")
            append_chat(f"", f"Rexode: {response_content}")
            time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            graceful_exit(None, None)
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")
            console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
            console.print(f"[dim]Mode: {model_name}[/dim]", justify="right")
            append_chat(f"", f"Rexode: {response_content}")
            time.sleep(2)

        except (KeyboardInterrupt, EOFError):
            graceful_exit(None, None)
        except Exception as e:
            console.print(f"Error: {e}", style="bold red")

if __name__ == "__main__":
    asyncio.run(main())