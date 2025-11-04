from .server import run_mcp_server

def main():
    """Run the MCP server."""
    import sys
    import click

    # If run as CLI (e.g., via `uv run ...`), Click will handle args
    if len(sys.argv) > 1:
        run_mcp_server()  # Click parses the CLI args
    else:
        # If no args provided (e.g., started by Copilot from public registry),
        # run default startup explicitly with stdio transport
        ctx = click.Context(run_mcp_server)
        ctx.params = {"port": 8000, "transport": "stdio"}
        run_mcp_server.callback(**ctx.params)