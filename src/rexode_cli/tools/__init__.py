# src/rexode_cli/tools/__init__.py

tool_registry = {
    "open_application": lambda app_name: f"Simulating opening {app_name}",
    "launch_app": lambda app_name: f"Simulating launching {app_name}",
    # Add other tools as needed for testing AIOperator
}