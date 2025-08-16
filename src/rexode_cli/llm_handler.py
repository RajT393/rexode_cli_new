from getpass import getpass
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
import os
import json

class LLMHandler:
    def __init__(self):
        pass

    def initialize_llm(self, llm_type: str, provider: str = None, model_name: str = None):
        if llm_type == "local":
            if not model_name:
                model_name = os.getenv("LOCAL_LLM_MODEL", "llama2")
            try:
                llm = Ollama(model=model_name)
                print(f"✅ Local LLM '{model_name}' initialized.")
                return llm
            except Exception as e:
                print(f"❌ Failed to initialize Local LLM: {e}")
                return None
        elif llm_type == "online":
            if not provider:
                provider = os.getenv("ONLINE_LLM_PROVIDER", "openai").lower()
            else:
                provider = provider.lower()

            api_key = self.get_api_key(provider)
            if not api_key:
                return None

            if not model_name:
                model_name = self.get_default_model(provider)

            try:
                if provider == "openai":
                    llm = ChatOpenAI(model_name=model_name, openai_api_key=api_key)
                elif provider == "google":
                    llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
                elif provider in ["openrouter", "anthropic", "meta-llama", "mistral", "llama3", "claude"]:
                    llm = ChatOpenAI(
                        model_name=model_name,
                        openai_api_key=api_key,
                        openai_api_base="https://openrouter.ai/api/v1"
                    )
                elif provider == "groq":
                    llm = ChatOpenAI(
                        model_name=model_name,
                        openai_api_key=api_key,
                        openai_api_base="https://api.groq.com/openai/v1"
                    )
                else:
                    print(f"❌ Unsupported online LLM provider: {provider}.")
                    return None
                print(f"✅ Online LLM '{model_name}' from '{provider}' initialized.")
                return llm
            except Exception as e:
                print(f"❌ Failed to initialize Online LLM: {e}")
                return None
        else:
            print("❌ Invalid LLM type specified.")
            return None

    def get_api_key(self, provider):
        api_key = os.getenv(f"{provider.upper()}_API_KEY")
        if not api_key:
            try:
                api_key = getpass(f"Enter {provider.upper()} API key (will be hidden): ")
            except Exception as e:
                print(f"❌ Could not read API key: {e}")
                return None
        return api_key

    def get_default_model(self, provider):
        if provider == "openai":
            return os.getenv("OPENAI_MODEL", "gpt-4")
        elif provider == "google":
            return os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
        elif provider == "anthropic":
            return os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
        else:
            return "default_online_model"

    def get_prompt(self, chat_history, tools):
        # Convert chat_history to a string format suitable for the prompt
        history_str = ""
        for entry in chat_history:
            if entry["role"] == "user":
                history_str += f"User: {entry['content']}\n"
            elif entry["role"] == "assistant":
                history_str += f"Assistant: {entry['content']}\n"
            elif entry["role"] == "tool":
                history_str += f"Tool Output: {entry['content']}\n"

        prompt = f"""You are Rexode, a helpful and powerful AI assistant. You have access to the following tools:

{json.dumps(tools, indent=2)}

Your goal is to assist the user by selecting and using the most appropriate tool(s) to fulfill their requests.

**Instructions:**
1.  **Tool Use:** If a tool is required, respond ONLY with a JSON object containing a "tool_calls" array. Each object in the array must have:
    *   `name`: The name of the tool to call.
    *   `parameters`: A JSON object containing the parameters for the tool.
    *   Example:
        ```json
        {{
          "tool_calls": [
            {{
              "name": "tool_name_here",
              "parameters": {{
                "param1": "value1",
                "param2": "value2"
              }}
            }}
          ]
        }}
        ```
2.  **Direct Response:** If no tool is needed, or if you have already used a tool and want to provide a final answer or ask for more information, respond ONLY with a JSON object containing a "response" key.
    *   Example:
        ```json
        {{
          "response": "Your direct response here."
        }}
        ```
3.  **Clarification:** If you need more information from the user to use a tool or provide a direct response, use the "response" format to ask for it.
4.  **ALWAYS return valid JSON.**

**Chat History:**
{history_str}

**User's Current Request:** {chat_history[-1]['content']}

**Your Response (JSON):**
"""
        return prompt

# Example usage (for testing purposes)
if __name__ == "__main__":
    handler = LLMHandler()
    # Test local LLM (requires Ollama running with 'llama2' model)
    # llm_local = handler.get_llm(llm_type="local", model_name="llama2")
    # if llm_local:
    #     print(llm_local.invoke("Hello, how are you?"))

    # Test online LLM (requires OPENAI_API_KEY environment variable)
    # llm_online = handler.get_llm(llm_type="online", model_name="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
    # if llm_online:
    #     print(llm_online.invoke("What is the capital of France?"))
