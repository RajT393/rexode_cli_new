import subprocess
import pyautogui
import time
import webbrowser
from .tools import tool_registry
from .utils import speak_text

class AIOperator:
    def __init__(self, model):
        self.model = model  # Gemini/LLM client
        self.memory = []    # short-term memory of tasks

    async def run(self, task: str):
        """
        Main entrypoint: interpret the task and decide how to execute it.
        """
        self.memory.append(task)

        # Step 1: Ask AI to classify the type of task
        classification_prompt = f"""
        You are an AI operator. A user asked: "{task}".
        Classify it into one of these categories:
        - CLI_COMMAND (run on terminal)
        - GUI_ACTION (screen automation like a human)
        - WEB_SEARCH (search internet and get info/code)
        - TOOL (use an existing Rexode tool)
        - PROJECT_BUILD (create/test/debug a full project)
        Respond with ONLY the category.
        """
        category = self.model.query(classification_prompt).strip().upper()
        speak_text(f"Task identified as {category}")

        # Step 2: Route to correct executor
        if category == "CLI_COMMAND":
            return await self._run_cli(task)
        elif category == "GUI_ACTION":
            return await self._run_gui(task)
        elif category == "WEB_SEARCH":
            return await self._run_web(task)
        elif category == "TOOL":
            return await self._run_tool(task)
        elif category == "PROJECT_BUILD":
            return await self._run_project(task)
        else:
            return f"Unknown task type for: {task}"

    async def _run_cli(self, task: str):
        try:
            speak_text("Executing in terminal")
            # Use asyncio.create_subprocess_shell for async execution
            process = await asyncio.create_subprocess_shell(
                task,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return f"CLI Command executed successfully.\nStdout: {stdout.decode().strip()}"
            else:
                return f"CLI Command failed.\nStdout: {stdout.decode().strip()}\nStderr: {stderr.decode().strip()}"
        except Exception as e:
            return f"CLI Error: {e}"

    async def _run_gui(self, task: str):
        """
        For GUI actions like 'open chrome and search for cats'.
        Uses pyautogui to simulate human-like interactions.
        """
        speak_text("Switching to GUI automation")
        time.sleep(1)
        pyautogui.typewrite(task, interval=0.05)
        pyautogui.press("enter")
        return f"GUI action executed: {task}"

    async def _run_web(self, task: str):
        """
        Open browser search if needed.
        """
        speak_text("Opening web for search")
        webbrowser.open(f"https://www.google.com/search?q={task}")
        return "Web search opened."

    async def _run_tool(self, task: str):
        """
        Match the user request to one of Rexode’s registered tools.
        """
        for name, tool_fn in tool_registry.items():
            if name.lower() in task.lower():
                speak_text(f"Using Rexode tool: {name}")
                # Assuming tool_fn might be async or sync
                if asyncio.iscoroutinefunction(tool_fn):
                    return await tool_fn(task)
                else:
                    return tool_fn(task)
        return "No matching tool found."

    async def _run_project(self, task: str):
        """
        For large 'make me a project' tasks.
        AI generates full solution plan and executes step by step.
        """
        speak_text("Starting autonomous project builder")
        plan_prompt = f"""
        User requested: {task}.
        Break it into clear executable steps:
        1. Gather requirements
        2. Search solutions
        3. Generate code
        4. Save to files
        5. Run & debug
        6. Report result
        """
        steps = self.model.query(plan_prompt)
        return f"Project plan ready:\n{steps}"
