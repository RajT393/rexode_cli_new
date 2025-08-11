import json
import os
from .tool_manager import ToolManager
from typing import Dict, Any, List, Type

# LangChain imports
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory # Corrected import
from langchain_core.tools import BaseTool # Use BaseTool for custom tools
from pydantic import BaseModel, Field # For defining tool input schemas

class RexodeTool(BaseTool):
    """Custom Tool for Rexode CLI."""
    name: str
    description: str
    args_schema: Type[BaseModel] = None # Use Pydantic model for args_schema
    orchestrator_instance: Any # Reference to the TaskOrchestrator instance

    async def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Use the ainvoke method for asynchronous execution."""
        return await self.orchestrator_instance._execute_tool(self.name, kwargs)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Use the ainvoke method for asynchronous execution."""
        return await self.orchestrator_instance._execute_tool(self.name, kwargs)

class TaskOrchestrator:
    def __init__(self, tool_manager: ToolManager, llm=None, llm_mode: str = "local_tools_only"):
        self.tool_manager = tool_manager
        self.llm = llm
        self.llm_mode = llm_mode # "local_llm", "online_llm", "local_tools_only"
        self.system_prompt = self._load_system_prompt()
        self.tools_json_schema = self._generate_tools_json_schema()

        self.agent_executor = None
        self.message_history = ChatMessageHistory()

        if self.llm_mode in ["local_llm", "online_llm"] and self.llm:
            # Prepare tools for LangChain agent
            langchain_tools = []
            for tool_name in self.tool_manager.get_all_tool_names():
                tool_def = self.tool_manager.get_tool_definition(tool_name)
                if tool_def:
                    # Dynamically create a Pydantic model for args_schema
                    # This is crucial for create_tool_calling_agent
                    schema_properties = {}
                    schema_required = []
                    if "parameters" in tool_def and "properties" in tool_def["parameters"]:
                        for prop_name, prop_def in tool_def["parameters"]["properties"].items():
                            # Map JSON schema types to Python types for Pydantic
                            py_type = self._map_json_type_to_python_type(prop_def.get("type"))
                            schema_properties[prop_name] = (
                                py_type,
                                Field(..., description=prop_def.get("description", ""))
                            )
                        if "required" in tool_def["parameters"]:
                            schema_required = tool_def["parameters"]["required"]

                    DynamicArgsSchema = self._create_dynamic_pydantic_model(
                        f"{tool_name.capitalize()}Args",
                        schema_properties,
                        schema_required
                    )

                    langchain_tools.append(
                        RexodeTool(
                            name=tool_name,
                            description=tool_def.get("description", ""),
                            args_schema=DynamicArgsSchema,
                            orchestrator_instance=self
                        )
                    )

            # Create the LangChain prompt template
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt.replace("{tools_json_schema}", self.tools_json_schema)),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                    MessagesPlaceholder(variable_name="agent_scratchpad"),
                ]
            )

            # Create the LangChain agent
            agent = create_tool_calling_agent(self.llm, langchain_tools, prompt)
            self.agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True)

            # Add message history
            self.agent_executor = RunnableWithMessageHistory(
                self.agent_executor,
                lambda session_id: self.message_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )

    def _map_json_type_to_python_type(self, json_type: str) -> Type:
        """Maps JSON schema types to Python types for Pydantic models."""
        if json_type == "string":
            return str
        elif json_type == "integer":
            return int
        elif json_type == "boolean":
            return bool
        elif json_type == "number":
            return float
        elif json_type == "array":
            return List[Any] # Or more specific list type if known
        elif json_type == "object":
            return Dict[str, Any] # Or more specific dict type if known
        else:
            return Any # Default to Any for unknown types

    def _create_dynamic_pydantic_model(self, name: str, properties: Dict[str, Any], required: List[str]) -> Type[BaseModel]:
        """Dynamically creates a Pydantic model."""
        # Create a dictionary for the model's fields
        fields = {}
        for prop_name, prop_type_field in properties.items():
            fields[prop_name] = prop_type_field

        # Create the Pydantic model
        DynamicModel = type(name, (BaseModel,), fields)

        # Set required fields
        for req_field in required:
            if req_field in DynamicModel.__fields__:
                DynamicModel.__fields__[req_field].required = True
        
        return DynamicModel

    def _load_system_prompt(self) -> str:
        """Loads the system prompt from system_prompt.txt."""
        prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "prompts", "system_prompt.txt")
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: system_prompt.txt not found at {prompt_path}")
            return "You are a helpful AI assistant."

    def _generate_tools_json_schema(self) -> str:
        """Generates a JSON string of available tools for the system prompt."""
        tools_for_schema = []
        for tool_name in self.tool_manager.get_all_tool_names():
            tool_def = self.tool_manager.get_tool_definition(tool_name)
            if tool_def:
                tools_for_schema.append({
                    "name": tool_def.get("name"),
                    "description": tool_def.get("description"),
                    "parameters": tool_def.get("parameters")
                })
        return json.dumps(tools_for_schema, indent=2)

    async def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """
        Executes a tool or delegates to an external agent.
        This is a placeholder for actual tool execution logic.
        """
        tool_def = self.tool_manager.get_tool_definition(tool_name)
        if not tool_def:
            return f"Error: Tool '{tool_name}' not found."

        # --- Agent Collaboration Placeholder ---
        # In a real scenario, you might check if this tool needs to be delegated
        # to an external agent or if it's a built-in tool.
        # For example:
        # if tool_name in ["external_agent_tool_1", "external_agent_tool_2"]:
        #     return await self._delegate_to_external_agent(tool_name, parameters)
        # ---------------------------------------

        # Simulate tool execution for now
        param_str = ", ".join([f"{k}='{v}'" for k, v in parameters.items()])
        return f"Executing tool '{tool_name}' with params: {param_str}. (Simulated success)"

    async def process_task(self, user_input: str) -> str:
        """
        Processes a user task, orchestrating tool usage and interaction.
        """
        if self.llm_mode in ["local_llm", "online_llm"] and self.llm:
            if not self.agent_executor:
                return "Error: LLM agent not initialized."
            
            try:
                # Attempt to get a response from the agent (which might involve tool calling)
                agent_response = await self.agent_executor.ainvoke(
                    {"input": user_input},
                    config={"configurable": {"session_id": "any_session_id"}} # Session ID for history
                )
                
                # Check if the agent actually used a tool
                # This is a heuristic: if the output is a simulated tool execution message,
                # or if there are tool outputs in intermediate steps.
                # For now, we'll rely on the simulated output string.
                if "Executing tool" in agent_response["output"] and "(Simulated success)" in agent_response["output"]:
                    return agent_response["output"]
                else:
                    # If the agent did not execute a tool, try to get a direct conversational response from the LLM
                    messages = [
                        {"role": "system", "content": "You are a helpful AI assistant. Answer the user's question directly."},
                        {"role": "user", "content": user_input}
                    ]
                    direct_llm_response = await self.llm.ainvoke(messages)
                    return direct_llm_response.content
                
            except Exception as e:
                return f"Error processing with LLM agent ({self.llm_mode}): {e}"
        else:
            # Rule-based intent parsing for "Local Tools Only" mode
            user_input_lower = user_input.lower()
            
            # Simple intent parsing for demonstration
            if "use example tool 1" in user_input_lower:
                tool_name = "example_tool_1"
                # Simulate parameter extraction (will be done by LLM later)
                param1_value = "default_value_1"
                param2_value = 0
                if "with value" in user_input_lower:
                    parts = user_input_lower.split("with value")
                    if len(parts) > 1:
                        param_str = parts[1].strip()
                        if "and" in param_str:
                            p_parts = param_str.split("and")
                            param1_value = p_parts[0].strip()
                            try:
                                param2_value = int(p_parts[1].strip())
                            except ValueError:
                                pass
                parameters = {"param1": param1_value, "param2": param2_value}
                return await self._execute_tool(tool_name, parameters)

            elif "search for" in user_input_lower:
                tool_name = "example_tool_2"
                query = user_input_lower.replace("search for", "").strip().strip("'\"")
                parameters = {"query": query}
                if query:
                    return await self._execute_tool(tool_name, parameters)
                else:
                    return "Please provide a query for the search."
            elif "say hello to" in user_input_lower: # Rule for the new say_hello tool
                tool_name = "say_hello"
                name = user_input_lower.replace("say hello to", "").strip().capitalize()
                parameters = {"name": name}
                if name:
                    return await self._execute_tool(tool_name, parameters)
                else:
                    return "Please provide a name to say hello to."
            else:
                return "I'm not sure how to handle that request. Please try a different command or ask for help."
