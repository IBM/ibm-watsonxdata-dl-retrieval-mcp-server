import sys
import logging
import os
import anyio
import click
import mcp.types as types
from .document_library_api import get_document_library_list
from .retrival_service_api import watsonx_data_query_handler
from fastmcp.server.server import FastMCP
from mcp.types import Tool as MCPTool


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

class mcp_server(FastMCP):
    async def _list_tools_mcp(self) -> list[MCPTool]:
        logger.info("=== Entered _mcp_list_tools() ===")
        tool_definitions = []

        # Step 1: Retrieve document libraries
        try:
            document_library_definitions = get_document_library_list()
            logger.info(f"Retrieved document libraries: {document_library_definitions}")
        except Exception as e:
            logger.error(f"Error while fetching document libraries: {e}", exc_info=True)
            return []

        # Step 2: Check if the result is empty
        if not document_library_definitions:
            logger.warning("⚠️ No document libraries found from get_document_library_list()")
            return []

        logger.info(f"Found {len(document_library_definitions)} document libraries. Processing...")

        # Step 3: Loop through libraries and build tools
        for idx, tool_config in enumerate(document_library_definitions, start=1):
            logger.debug(f"[{idx}] Raw tool config: {tool_config}")

            if not isinstance(tool_config, dict):
                logger.warning(f"[{idx}] Skipping invalid entry (not a dict): {tool_config}")
                continue

            name_part = tool_config.get('document_library_name')
            id_part = tool_config.get('document_library_id')
            if not name_part or not id_part:
                logger.warning(f"[{idx}] Missing required fields in config: {tool_config}")
                continue

            tool_name = (name_part + id_part).replace("-", "_").replace(" ", "_")
            logger.info(f"[{idx}] Constructed tool name: {tool_name}")

            try:
                tool_def = types.Tool(
                    name=tool_name,
                    description=tool_config.get('document_library_description', "No description provided"),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"},
                        },
                        "required": ["query"]
                    }
                )
                tool_definitions.append(tool_def)
                logger.info(f"[{idx}] ✅ Added tool: {tool_name}")
            except Exception as e:
                logger.error(f"[{idx}] ❌ Failed to add tool {tool_name}: {e}", exc_info=True)

        # Step 4: Summary log
        logger.info(f"=== Completed tool listing: {len(tool_definitions)} tools discovered ===")

        return tool_definitions

    
    async def _call_tool_mcp(
        self,
        name: str,
        arguments: dict
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        document_library_definitions = get_document_library_list()
        logger.info(f"Document library list : {document_library_definitions}")

        for tool_config in document_library_definitions:
            if not isinstance(tool_config, dict):
                logger.info(
                    f"Skipping invalid entry in document libraries (not a dictionary): {tool_config}")
                continue
            tool_name = (tool_config.get('document_library_name') + tool_config.get(
                'document_library_id')).replace("-", "_").replace(" ", "_")
            logger.info(f"Document library tool name : {tool_name}")
            if tool_name == name:
                query = arguments["query"]
                try:
                    result = watsonx_data_query_handler(query, tool_config.get(
                        'document_library_id'), tool_config.get('container_type'), tool_config.get('container_id'))
                    return [types.TextContent(type="text", text=result)]
                except Exception as e:
                    logger.error(
                        f"Error calling tool '{name}' with query '{query}': {e}", exc_info=True)
                    return [types.TextContent(type="text", text=f"Error executing tool '{name}': {str(e)}")]
        logger.error(f"Tool not found: {name}")
        return [types.TextContent(type="text", text=f"Tool not found: {name}, toolname {tool_name}")]

app = mcp_server("ibm-watsonxdata-dl-retrieval-mcp-server")
    
@click.command()
@click.version_option()
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option("--transport", type=click.Choice(["stdio", "sse"]), default="sse", help="Transport type")
def run_mcp_server(port: int, transport: str):
    """Runs the MCP server."""
    logger.info(">>> Entered run_mcp_server()")
    logger.info(f"Transport = {transport}, Port = {port}")

    # ✅ Log configured environment variables (with masking for sensitive values)
    env_keys = [
        "LH_CONTEXT",
        "WATSONX_DATA_RETRIEVAL_ENDPOINT",
        "DOCUMENT_LIBRARY_API_ENDPOINT",
        "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT",
        "WATSONX_DATA_API_KEY",
    ]

    env_values = {k: os.getenv(k) for k in env_keys}

    # Mask sensitive entries
    if env_values.get("WATSONX_DATA_API_KEY"):
        env_values["WATSONX_DATA_API_KEY"] = "***MASKED***"

    logger.info(f"Loaded environment variables: {env_values}")

    if transport == "sse":
        logger.info(f"Starting MCP server with SSE transport on port {port}...")
        async def arun():
            await app.run_sse_async(
                host="127.0.0.1",
                port=port,
                log_level=(os.getenv("LOG_LEVEL", "").upper() == "DEBUG"),
            )

        try:
            logger.debug("Running SSE async loop via anyio.run()")
            anyio.run(arun)
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user (KeyboardInterrupt).")
        except Exception as e:
            logger.error(f"❌ SSE server failed: {e}", exc_info=True)

    elif transport == "stdio":
        logger.info("Starting MCP server with stdio transport")
        async def arun():
            await app.run_async("stdio")

        try:
            logger.debug("Running STDIO async loop via anyio.run()")
            anyio.run(arun)
        except KeyboardInterrupt:
            logger.info("🛑 Server stopped by user (KeyboardInterrupt).")
        except Exception as e:
            logger.error(f"❌ STDIO server failed: {e}", exc_info=True)

    else:
        logger.critical(f"🚨 Unknown transport: {transport}")
        sys.exit(1)

