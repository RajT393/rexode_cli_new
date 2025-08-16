import re

def detect_tool(user_input: str):
    text = user_input.lower()

    if re.search(r"(open|launch|start).*(whatsapp)", text):
        return "open_application", {"application_name": "whatsapp"}

    if re.search(r"(open|launch|start).*(youtube)", text):
        return "open_application", {"application_name": "youtube"}

    # fallback
    return None, None