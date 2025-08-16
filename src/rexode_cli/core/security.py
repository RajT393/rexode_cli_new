from rich.console import Console

def request_confirmation(action):
    """Asks the user for confirmation before performing an action."""
    console = Console()
    console.print(f"[bold yellow]Warning:[/bold yellow] You are about to {action}.", style="yellow")
    confirmation = console.input("Are you sure you want to continue? (y/n): ").lower()
    return confirmation == 'y'
