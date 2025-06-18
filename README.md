
# Watsonx.data Document Library Retrieval MCP Server

The **Watsonx.data Document Library Retrieval MCP Server** is a Model Context Protocol (MCP)-compliant service that seamlessly connects AI agents with document libraries in watsonx.data, enabling intelligent data retrieval and interaction.

## Key Features

- **Dynamic Discovery & Registration**  
  Automatically detects and registers document libraries as MCP tools.

- **Natural Language Interface**  
  Query document libraries using conversational language and receive human-readable responses.

- **Minimal Configuration**  
  Deploy with simple setup requirements and zero complex configurations.

- **Framework-Agnostic Integration**  
  Plug directly into the preferred agentic frameworks with native MCP compatibility.

---

## Overview

- **Protocol**: Model Context Protocol (MCP)  
- **Purpose**: Acts as a bridge between agentic AI frameworks and watsonx.data document libraries  
- **Supported Environments**: IBM Cloud Pak for Data (CPD), Watsonx SaaS  
- **Agent Compatibility**: The agentic framework must support the MCP standard (via SSE or Stdio).  
  _Note: This server will not function with agents that do not support MCP._

---

## Prerequisites

- Python version **3.11** or later  
- Access to your **CPD or SaaS environment**  
- Access credentials and a **CA certificate bundle** for CPD  
- Ensure your **agent framework supports MCP protocol**

---

## Getting CA Bundle for CPD

1. Login to your OpenShift cluster:

    ```bash
    oc login -u kubeadmin -p '<your_openshift_password>' https://<your_openshift_cpd_url>:6443
    ```

2. Extract the root CA bundle:

    ```bash
    oc get configmap kube-root-ca.crt -o jsonpath='{.data.ca\.crt}' > cabundle.crt
    ```

---

## Setup

### Step 1: Install Python

- Official Installer: [https://www.python.org/downloads/](https://www.python.org/downloads/)

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

### Step 3: Activate the virtual environment

```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Step 4: Install the `uv` package manager

```bash
pip install uv
```

- `uv` package: [https://pypi.org/project/uv/](https://pypi.org/project/uv/)

---

## Configuration

### For Cloud Pak for Data (CPD):

```bash
export CPD_ENDPOINT="<cpd-endpoint>"
export CPD_USERNAME="<cpd-username>"
export CPD_PASSWORD="<cpd-password>"
export CA_BUNDLE_PATH="<absolute_path_to_cabundle.crt>"
export LH_CONTEXT="CPD"
```

### For Watsonx SaaS:

```bash
export WATSONX_DATA_API_KEY="<api-key>"
export WATSONX_DATA_RETRIEVAL_ENDPOINT="<retrieval-service-endpoint>"
export DOCUMENT_LIBRARY_API_ENDPOINT="<document-library-endpoint>"
export WATSONX_DATA_TOKEN_GENERATION_ENDPOINT="<token-generation-endpoint>"
export LH_CONTEXT="SAAS"
```

---

## Running the Server

```bash
uv run ibm-watsonxdata-dl-retrieval-mcp-server
```

By default, the server runs in `sse` transport mode on port 8000.

### Transport: SSE

```bash
uv run ibm-watsonxdata-dl-retrieval-mcp-server --port <desired_port> --transport sse
```

### Transport: stdio

```bash
uv run ibm-watsonxdata-dl-retrieval-mcp-server --port <desired_port> --transport stdio
```

---

## Integrating with Agentic Frameworks

This server supports standard MCP adapters, compatible with most modern agentic frameworks. These adapters expose tools via:

- HTTP endpoints (e.g., `http://localhost:8000/sse`)
- OR through `stdio`.

### Example (Python + LlamaStack)

```python
from llama_stack.distribution.library_client import LlamaStackAsLibraryClient
from llama_stack_client.types.toolgroup_register_params import McpEndpoint

client = LlamaStackAsLibraryClient("your-inference-provider")
client.initialize()

client.toolgroups.register(
    toolgroup_id="mcp::your_toolgroup",
    provider_id="model-context-protocol",
    mcp_endpoint=McpEndpoint(uri="http://localhost:8000/sse"),
)
```

Once registered, tools can be used as part of an agent definition:

```python
from llama_stack_client import Agent

agent = Agent(
    client,
    model="your-model",
    instructions="...",
    tools=["mcp::your_toolgroup"],
)
```

📚 [LlamaStack Docs – Model Context Protocol](https://llama-stack.readthedocs.io/en/latest/building_applications/tools.html#model-context-protocol-mcp)

---

## Limitations

- Environment credentials **cannot be changed during runtime**.
  - To change credentials, either:
    - Start a new server with new env variables, OR
    - Source new environment variables and restart the server.

### Tool Naming

Each document library is registered with a unique tool name:

> `tool_name = <library_name><library_id>`

Example:

```bash
invoice_document_library77e4b4dd_479e_4406_acc4_ce154c96266c
```