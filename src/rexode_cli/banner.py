import os
import sys
import codecs

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

def print_banner():
    os.system("chcp 65001 > nul")
    banner = """
██████╗ ███████╗██╗  ██╗ ██████╗ ██████╗ ███████╗
██╔══██╗██╔════╝╚██╗██╔╝██╔═══██╗██╔══██╗██╔════╝
██████╔╝█████╗   ╚███╔╝ ██║   ██║██║  ██║█████╗  
██╔══██╗██╔══╝    ███╗  ██║   ██║██║  ██║██╔══╝  
██║  ██║███████╗██╔╝ ██╗╚██████╔╝██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝
REXODE CLI - Your all-in-one AI assistant 🧠⚡
    """
    print(banner)
    print("💡 Tip: Press Ctrl+Alt+M to switch modes | Ctrl+Alt+S for screen OCR\n")

