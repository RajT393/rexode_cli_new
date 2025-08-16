import re
from .tool_manager import ToolManager
from ..llm_handler import LLMHandler
from .security import request_confirmation
from .logging import log_action
import json
import shlex
from fuzzywuzzy import fuzz, process
from rich.console import Console
from parse import parse

class TaskOrchestrator:
    def __init__(self, tool_manager: ToolManager, llm=None, llm_mode=None, llm_handler: LLMHandler = None):
        self.tool_manager = tool_manager
        self.llm = llm
        self.llm_mode = llm_mode
        self.llm_handler = llm_handler
        self.history = []
        self.console = Console()

    async def process_task(self, user_input):
        self.is_cancelled = False
        if self.llm:
            # LLM mode: Use the LLM to determine the tool to use
            return await self.process_with_llm(user_input)
        else:
            # No LLM mode: Use a rule-based approach
            return self.process_with_rules(user_input)

    def get_tool_info(self, tool_name):
        for category in self.tool_manager.tools:
            for tool_info in category['tools']:
                if tool_info['name'] == tool_name:
                    return tool_info
        return None

    def fallback(self, tool_name, parameters, error=None):
        if error:
            log_action(f"Tool '{tool_name}' failed with error: {error}. Attempting fallback.")
            self.console.print(f"[yellow]... Tool '{tool_name}' failed. Attempting fallback...[/yellow]")
        else:
            log_action(f"Tool '{tool_name}' not found, attempting fallback.")
            self.console.print(f"[yellow]... Tool '{tool_name}' not found. Attempting fallback...[/yellow]")
        
        # Fallback for OS & File Management (existing logic)
        if tool_name in ["list_files", "read_file", "write_file", "delete_file"]:
            try:
                # Attempt to use execute_shell_command as a fallback
                shell_command = None
                if tool_name == "list_files":
                    shell_command = f"ls {parameters.get('path', '.')}"
                elif tool_name == "read_file":
                    shell_command = f"cat {parameters.get('file_path')}"
                elif tool_name == "write_file":
                    shell_command = f"echo \"{parameters.get('content')}\" > {parameters.get('file_path')}"
                elif tool_name == "delete_file":
                    shell_command = f"rm {parameters.get('file_path')}"
                
                if shell_command:
                    result = self.tool_manager.get_tool("execute_shell_command")(shell_command)
                    self.console.print(f"[green]V Fallback to 'execute_shell_command' for {tool_name} successful.[/green]")
                    return result
            except Exception as e:
                self.console.print(f"[red]x Fallback to 'execute_shell_command' for {tool_name} failed: {e}[/red]")
                return f"Fallback failed: {e}"

        # Fallback for Web & Data Access (enhanced)
        if tool_name in ["search_web", "scrape_website", "get_news", "get_weather"]:
            try:
                query = parameters.get("query") or parameters.get("topic") or parameters.get("location")
                url = parameters.get("url")

                if query and self.tool_manager.get_tool("search_web"):
                    self.console.print(f"[yellow]... Attempting web search for: {query}[/yellow]")
                    search_results = self.tool_manager.get_tool("search_web")(query)
                    self.console.print(f"[green]V Web search successful.[/green]")
                    if search_results and self.tool_manager.get_tool("scrape_website"):
                        first_link = search_results[0].get("link") # Assuming search_web returns list of dicts with 'link'
                        if first_link:
                            self.console.print(f"[yellow]... Attempting to scrape: {first_link}[/yellow]")
                            scraped_content = self.tool_manager.get_tool("scrape_website")(first_link)
                            self.console.print(f"[green]V Website scraping successful.[/green]")
                            return scraped_content
                    return search_results
                elif url and self.tool_manager.get_tool("scrape_website"):
                    self.console.print(f"[yellow]... Attempting to scrape: {url}[/yellow]")
                    scraped_content = self.tool_manager.get_tool("scrape_website")(url)
                    self.console.print(f"[green]V Website scraping successful.[/green]")
                    return scraped_content
            except Exception as e:
                self.console.print(f"[red]x Web/Scraping fallback failed: {e}[/red]")
                return f"Web/Scraping fallback failed: {e}"

        # Fallback for missing integrations (fetch_api_data)
        if tool_name in ["send_message", "schedule_task", "calendar_event", "fetch_api_data"]:
            try:
                api_url = parameters.get("api_url")
                if not api_url:
                    # Try to construct a generic API call if possible
                    # This is highly speculative and would need more context
                    self.console.print(f"[yellow]Could not determine API URL for {tool_name}. Cannot use fetch_api_data fallback.[/yellow]")
                    return f"Fallback failed: Could not determine API URL for {tool_name}."

                if self.tool_manager.get_tool("fetch_api_data"):
                    self.console.print(f"[yellow]... Attempting to fetch API data from: {api_url}[/yellow]")
                    api_data = self.tool_manager.get_tool("fetch_api_data")(api_url)
                    self.console.print(f"[green]V API data fetch successful.[/green]")
                    return api_data
            except Exception as e:
                self.console.print(f"[red]x API data fetch fallback failed: {e}[/red]")
                return f"API data fetch fallback failed: {e}"

        # Fallback for generating ad-hoc scripts (generate_code)
        if tool_name in ["generate_code", "analyze_data", "train_ml_model", "optimize_ml_model"]:
            try:
                prompt = f"Generate a Python script to perform a task similar to '{tool_name}' with parameters {parameters}. Focus on the core logic."
                if self.tool_manager.get_tool("generate_code"):
                    self.console.print(f"[yellow]... Attempting to generate code for '{tool_name}'...\nPrompt: {prompt}[/yellow]")
                    generated_code = self.tool_manager.get_tool("generate_code")(prompt=prompt, language="python")
                    self.console.print(f"[green]V Code generation successful.[/green]")
                    return generated_code
            except Exception as e:
                self.console.print(f"[red]x Code generation fallback failed: {e}[/red]")
                return f"Code generation fallback failed: {e}"

        # Generic fallback to execute_shell_command if applicable (existing logic)
        if self.tool_manager.get_tool("execute_shell_command"):
            self.console.print(f"[yellow]... No specific fallback for '{tool_name}'. Attempting generic shell command.[/yellow]")
            try:
                # Attempt a generic shell command if parameters look like a command
                if isinstance(parameters, dict) and "command" in parameters:
                    command = parameters["command"]
                elif isinstance(parameters, list) and len(parameters) > 0 and isinstance(parameters[0], str):
                    command = parameters[0]
                else:
                    return f"Tool '{tool_name}' not found and no suitable generic fallback command could be constructed."
                
                result = self.tool_manager.get_tool("execute_shell_command")(command)
                self.console.print(f"[green]V Fallback to generic shell command successful.[/green]")
                return result
            except Exception as e:
                self.console.print(f"[red]x Generic shell command fallback failed: {e}[/red]")
                return f"Tool '{tool_name}' not found and generic fallback failed: {e}"
        
        self.console.print(f"[red]x Tool '{tool_name}' not found and no fallback available.[/red]")
        return f"Tool '{tool_name}' not found and no fallback available."

    async def process_with_llm(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        while True:
            try:
                self.console.print("[yellow]... Rexode is thinking...[/yellow]")
                prompt = self.llm_handler.get_prompt(self.history, self.tool_manager.tools)
                response = await self.llm.ainvoke(prompt)
                self.history.append({"role": "assistant", "content": response.content})
                
                try:
                    tool_call = json.loads(response.content)
                except json.JSONDecodeError:
                    log_action(f"LLM returned invalid JSON: {response.content}")
                    self.console.print(f"[red]x LLM returned invalid response. Please try rephrasing your request.[/red]")
                    return "Error: LLM returned an unparseable response."

                if "tool_calls" in tool_call:
                    for tc in tool_call["tool_calls"]:
                        tool_name = tc['name']
                        parameters = tc['parameters']
                        
                        tool_info = self.get_tool_info(tool_name)
                        if tool_info and tool_info.get('sensitive'):
                            if not request_confirmation(f"execute the '{tool_name}' tool with parameters: {parameters}"):
                                log_action(f"User cancelled action: {tool_name}")
                                return "Action cancelled by user."

                        tool = self.tool_manager.get_tool(tool_name)
                        if tool:
                            self.console.print(f"[yellow]... Executing tool: {tool_name}...[/yellow]")
                            log_action(f"Executing tool: {tool_name} with parameters: {parameters}")
                            try:
                                result = tool(**parameters)
                                self.console.print(f"[green]V Tool '{tool_name}' executed successfully.[/green]")
                                if result is not None:
                                    self.console.print(f"[dim]Output:[/dim] {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}")
                                self.history.append({"role": "tool", "content": result})
                            except Exception as tool_e:
                                log_action(f"Error executing tool {tool_name}: {tool_e}")
                                self.console.print(f"[red]x Error executing tool '{tool_name}': {tool_e}[/red]")
                                self.history.append({"role": "tool", "content": f"Error executing tool {tool_name}: {tool_e}"})
                                # Attempt fallback on tool execution failure
                                self.console.print(f"[yellow]... Attempting fallback for '{tool_name}' due to execution error...[/yellow]")
                                result = self.fallback(tool_name, parameters, error=str(tool_e))
                                self.history.append({"role": "tool", "content": result})
                        else:
                            self.console.print(f"[red]x Tool '{tool_name}' not found.[/red]")
                            result = self.fallback(tool_name, parameters)
                            self.history.append({"role": "tool", "content": result})
                elif "response" in tool_call:
                    log_action(f"LLM response: {tool_call['response']}")
                    self.console.print(f"[green]V Rexode response: {tool_call['response']}[/green]")
                    return tool_call["response"]
                else:
                    log_action(f"LLM returned unexpected format: {response.content}")
                    self.console.print(f"[red]x LLM returned an unexpected format. Please try rephrasing your request.[/red]")
                    return "Error: LLM returned an unexpected format."

            except Exception as e:
                log_action(f"Unhandled error in LLM processing: {e}")
                self.console.print(f"[red]x An unexpected error occurred during LLM processing: {e}[/red]")
                return f"An unexpected error occurred: {e}"

    def _extract_parameters(self, user_input, tool_info):
        parameters = {}
        missing_params = []

        if 'properties' in tool_info['parameters']:
            for param_name, param_details in tool_info['parameters']['properties'].items():
                # Look for the parameter name followed by an equals sign
                param_pattern = rf'{param_name}='
                match = re.search(param_pattern, user_input, re.IGNORECASE)

                if match:
                    start_index = match.end()
                    value_str = user_input[start_index:].strip()

                    # Find the end of the current parameter's value
                    # This is either the start of the next parameter or the end of the string
                    end_index = len(value_str)
                    for other_param_name in tool_info['parameters']['properties']:
                        if other_param_name != param_name:
                            other_param_pattern = rf'{other_param_name}='
                            other_match = re.search(other_param_pattern, value_str, re.IGNORECASE)
                            if other_match and other_match.start() < end_index:
                                end_index = other_match.start()
                    
                    value = value_str[:end_index].strip()

                    # Remove quotes if present
                    if (value.startswith('"') and value.endswith('"')) or \
                       (value.startswith("'") and value.endswith("'")):
                        value = value[1:-1]

                    parameters[param_name] = value
                elif param_name in tool_info['parameters'].get('required', []):
                    missing_params.append(param_name)
        
        return parameters, missing_params

    def process_with_rules(self, user_input):
        if self.is_cancelled:
            return "Task cancelled by user."
        try:
            # Attempt to find the best matching tool using fuzzy matching
            all_tool_names = [t['name'] for category in self.tool_manager.tools for t in category['tools']]
            
            # Use the entire user_input to find the best tool match
            best_match = process.extractOne(user_input, all_tool_names, scorer=fuzz.token_set_ratio)

            tool_name = None
            if best_match and best_match[1] > 60:  # Threshold for a good match
                tool_name = best_match[0]
                self.console.print(f"[dim]Detected tool: {tool_name} (Confidence: {best_match[1]})[/dim]")
            else:
                self.console.print(f"[red]x No clear tool detected in your input. Please be more specific.[/red]")
                return "No tool detected."

            tool_info = self.get_tool_info(tool_name)
            if not tool_info: # Should not happen if tool_name came from all_tool_names
                self.console.print(f"[red]x Internal error: Tool '{tool_name}' not found after fuzzy match.[/red]")
                return "Internal error."

            parameters, missing_params = self._extract_parameters(user_input, tool_info)
            
            if missing_params:
                self.console.print(f"[yellow]I need more information to execute '{tool_name}'.[/yellow]")
                for param_name in missing_params:
                    param_details = tool_info['parameters']['properties'][param_name]
                    prompt_message = f"[bold green]Please provide value for '{param_name}' ({param_details.get('description', 'no description')}) (Type: {param_details.get('type', 'string')}): [/bold green]"
                    while True:
                        user_provided_value = self.console.input(prompt_message).strip()
                        if user_provided_value.lower() == 'cancel':
                            self.console.print("[red]Action cancelled by user.[/red]")
                            return "Action cancelled by user."
                        
                        # Attempt to convert and validate input
                        try:
                            if param_details.get('type') == 'integer':
                                user_provided_value = int(user_provided_value)
                            elif param_details.get('type') == 'number':
                                user_provided_value = float(user_provided_value)
                            elif param_details.get('type') == 'boolean':
                                if user_provided_value.lower() in ['true', 'yes']:
                                    user_provided_value = True
                                elif user_provided_value.lower() in ['false', 'no']:
                                    user_provided_value = False
                                else:
                                    raise ValueError("Invalid boolean value.")
                            elif param_details.get('type') == 'array':
                                user_provided_value = [item.strip() for item in user_provided_value.split(',')]

                            # Check enum if applicable
                            if 'enum' in param_details and user_provided_value not in param_details['enum']:
                                if isinstance(user_provided_value, list):
                                    user_provided_value = [item for item in user_provided_value if item in param_details['enum']]
                                    if not user_provided_value:
                                        raise ValueError(f"None of the provided values are valid for enum: {param_details['enum']}")
                                else:
                                    raise ValueError(f"Value not in allowed enum values: {param_details['enum']}")

                            parameters[param_name] = value.strip().strip("'").strip('"')
                            break # Exit inner loop if input is valid
                        except ValueError as ve:
                            self.console.print(f"[red]Invalid input for '{param_name}': {ve}. Please try again or type 'cancel'.[/red]")
                        except Exception as e:
                            self.console.print(f"[red]An unexpected error occurred during input for '{param_name}': {e}. Please try again or type 'cancel'.[/red]")

            if tool_info.get('sensitive'):
                if not request_confirmation(f"execute the '{tool_name}' tool with parameters: {parameters}"):
                    log_action(f"User cancelled action: {tool_name}")
                    return "Action cancelled by user."

            tool = self.tool_manager.get_tool(tool_name)

            if tool:
                self.console.print(f"[yellow]... Executing tool: {tool_name}...[/yellow]")
                log_action(f"Executing tool: {tool_name} with parameters: {parameters}")
                try:
                    result = tool(**parameters)
                    self.console.print(f"[green]V Tool '{tool_name}' executed successfully.[/green]")
                    if result is not None:
                        self.console.print(f"[dim]Output:[/dim] {str(result)[:500]}{'...' if len(str(result)) > 500 else ''}")
                    return result
                except Exception as tool_e:
                    log_action(f"Error executing tool {tool_name}: {tool_e}")
                    self.console.print(f"[red]x Error executing tool '{tool_name}': {tool_e}[/red]")
                    return self.fallback(tool_name, parameters, error=str(tool_e))
            else:
                self.console.print(f"[red]x Tool '{tool_name}' not found.[/red]")
                return self.fallback(tool_name, parameters)
        except Exception as e:
            log_action(f"Unhandled error in rule-based processing: {e}")
            self.console.print(f"[red]x An unexpected error occurred during rule-based processing: {e}[/red]")
            return f"An unexpected error occurred: {e}"
