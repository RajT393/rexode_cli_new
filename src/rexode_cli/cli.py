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


from .core.tool_manager import ToolManager
from .core.task_orchestrator import TaskOrchestrator
from .llm_handler import LLMHandler
from rich.console import Console
from rich.panel import Panel
from .inline_activity_indicator import InlineActivityIndicator
from langchain.callbacks.base import BaseCallbackHandler
from .core.config import Config


class CLI:
    def __init__(self):
        self.console = Console()
        self.llm_handler = LLMHandler()
        self.tool_manager = None
        self.orchestrator = None
        self.mode = None
        self.model_name = None
        self.llm = None
        self.chat_mode = "text"
        self.config = Config()
        self.exit_confirmed = False
        self.should_exit = False
        self.cancel_event = threading.Event()

    def on_press(self, key):
        try:
            if key == keyboard.Key.esc:
                if self.orchestrator:
                    self.orchestrator.cancel()
                return False
        except AttributeError:
            pass

    def graceful_exit(self, sig, frame):
        self.console.print("\nGoodbye from Rexode.", style="bold red")
        sys.exit(0)

    

    def select_mode(self):
        self.console.print("\nSelect an LLM Mode:", style="bold blue")
        self.console.print("  1. Local LLM (e.g., Ollama, Llama.cpp)", style="blue")
        self.console.print("  2. Online LLM (e.g., OpenAI, Google Gemini, Anthropic) - Requires API Key", style="blue")
        self.console.print("  3. Local Tools Only (No LLM - Rule-based intent parser)", style="blue")
        
        while True:
            selected_mode = self.console.input("[bold green]Enter your choice (1, 2, or 3): [/bold green]").strip()
            if selected_mode in ["1", "2", "3"]:
                break
            self.console.print("Invalid choice. Please enter 1, 2, or 3.", style="bold red")

        if selected_mode == "1":
            self.console.print("Local LLM mode selected.", style="bold green")
            self.model_name = self.console.input("[bold green]Enter local model name (e.g., llama2, mistral): [/bold green]").strip()
            self.llm = self.llm_handler.initialize_llm(llm_type="local", model_name=self.model_name)
        elif selected_mode == "2":
            self.console.print("Online LLM mode selected.", style="bold green")
            provider = self.console.input("[bold green]Enter online LLM provider (e.g., openai, google, anthropic): [/bold green]").strip().lower()
            self.model_name = self.console.input("[bold green]Enter model name (e.g., gpt-4, gemini-1.5-pro): [/bold green]").strip()
            self.llm = self.llm_handler.initialize_llm(llm_type="online", provider=provider, model_name=self.model_name)
        elif selected_mode == "3":
            self.console.print("Local Tools Only mode selected.", style="bold green")
            self.model_name = "local_tools_only"
            self.llm = None
        
        if self.llm is None and selected_mode != "3":
            self.console.print("Failed to initialize LLM. Exiting.", style="bold red")
            sys.exit(1)

        return selected_mode

    async def run(self):
        signal.signal(signal.SIGINT, self.graceful_exit)
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        print_banner()
        ensure_log_folder()
        

        #         if not is_subscription_active():
#             enforce_subscription()

#         activate_trial()

        os.makedirs("config", exist_ok=True)
        
        load_mode()
        mode_config = get_mode_config()

        permissions = load_permissions()

        threading.Thread(target=listen_for_shortcuts, daemon=True).start()

        self.console.print("Rexode is ready!", style="bold green")

        self.mode = self.select_mode()
        

        self.tool_manager = ToolManager(self.config)
        self.orchestrator = TaskOrchestrator(self.tool_manager, llm=self.llm, llm_mode=self.model_name, llm_handler=self.llm_handler)

        agent_indicator = InlineActivityIndicator(self.console, "Rexode is thinking...")

        while True:
            try:
                response_content = ""
                if self.chat_mode == "voice":
                    user_input = get_voice_input()
                    if not user_input:
                        continue
                    self.console.print(Panel(user_input, title="You", title_align="left", border_style="blue"))
                else:
                    user_input = self.console.input(f"You ({self.model_name})> ").strip()

                if user_input.lower() in ["exit", "quit", "bye"]:
                    self.console.print("Goodbye from Rexode.", style="bold red")
                    break

                append_chat(f"You: {user_input}", f"")
                
                agent_indicator.start()
                
                response_content = await self.orchestrator.process_task(user_input)

                agent_indicator.stop()
                self.console.print()
                

                self.console.print(Panel(response_content, title="Rexode", title_align="left", border_style="green"))
                self.console.print(f"[dim]Mode: {self.model_name}[/dim]", justify="right")
                append_chat(f"", f"Rexode: {response_content}")
                

            except (KeyboardInterrupt, EOFError):
                self.graceful_exit(None, None)
            except Exception as e:
                self.console.print(f"Error: {e}", style="bold red")