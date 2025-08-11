from getpass import getpass
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
import os

class LLMHandler:
    def __init__(self):
        pass

    def get_llm(self, llm_type: str, model_name: str = None, api_key: str = None, provider: str = None):
        llm = None
        if llm_type == "local":
            if not model_name:
                model_name = os.getenv("LOCAL_LLM_MODEL", "llama2") # Default to llama2
            llm = Ollama(model=model_name)
            print(f"✅ Local LLM '{model_name}' initialized.")
        elif llm_type == "online":
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    api_key = getpass("Enter API key (will be hidden): ")

            # Use provided provider, or fallback to environment variable/default
            if not provider:
                provider = os.getenv("ONLINE_LLM_PROVIDER", "openai").lower() # Default to openai
            else:
                provider = provider.lower()

            if not model_name:
                if provider == "openai":
                    model_name = os.getenv("OPENAI_MODEL", "gpt-4")
                elif provider == "google":
                    model_name = os.getenv("GOOGLE_MODEL", "gemini-1.5-pro")
                elif provider == "anthropic":
                    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
                else:
                    model_name = "default_online_model" # Fallback

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
        else:
            print("❌ Invalid LLM type specified.")
            return None
        return llm

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
