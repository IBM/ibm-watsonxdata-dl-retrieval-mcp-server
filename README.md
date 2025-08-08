
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

NOTE: Please use open shift login command. The user and password will be open shift portal login username and password 

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

### Step 5: Install the MCP server package

```bash
pip install ibm-watsonxdata-dl-retrieval-mcp-server
```

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
NOTE:
* For CPD_ENDPOINT use endpoint url for installed CPD. Example: "https://cpd-cpd-instance.apps.perf10.5y2z.openshiftapps.com" 
* For CPD_USERNAME and CPD_PASSWORD use the username and password used to login to CPD.

### For Watsonx SaaS:

```bash
export WATSONX_DATA_API_KEY="<api-key>"
export WATSONX_DATA_RETRIEVAL_ENDPOINT="<retrieval-service-endpoint>"
export DOCUMENT_LIBRARY_API_ENDPOINT="<document-library-endpoint>"
export WATSONX_DATA_TOKEN_GENERATION_ENDPOINT="<token-generation-endpoint>"
export LH_CONTEXT="SAAS"
```
NOTE: 
* For DOCUMENT_LIBRARY_API_ENDPOINT please use the endpoint url corresponding to region from here: https://cloud.ibm.com/apidocs/data-ai-common-core#endpoint-url.
Example: https://api.ca-tor.dai.cloud.ibm.com 
* For WATSONX_DATA_RETRIEVAL_ENDPOINT please use the watsonx.data endpoint.
Example : https://console-ibm-cator.lakehouse.saas.ibm.com 
* For WATSONX_DATA_TOKEN_GENERATION_ENDPOINT please use the endpoint url from here: https://cloud.ibm.com/apidocs/iam-identity-token-api#endpoints .
Example: https://iam.cloud.ibm.com 

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

## Integrating with WXO 

Prerequisite:  

Install WXO ADK and complete the initial setup. Refer documentation for more details: https://developer.watson-orchestrate.ibm.com 

### Transport: STDIO

To add the MCP server in stdio transport with WXO refer the example below.

1. create connection
```bash 
orchestrate connections add -a <app id>
``` 
2. Configure connection
```bash 
orchestrate connections configure --app-id <app id> --environment draft -t team -k key_value
```
3. Setting credentials
```bash 
orchestrate connections set-credentials --app-id=<app id> --env draft -e WATSONX_DATA_API_KEY="<api_key>" -e WATSONX_DATA_RETRIEVAL_ENDPOINT="<wxd retrieval endpoint>" -e DOCUMENT_LIBRARY_API_ENDPOINT="<DL endpoint>" -e WATSONX_DATA_TOKEN_GENERATION_ENDPOINT="<token generation endpoint>" -e LH_CONTEXT="SAAS"
```
Example for Saas: 
```bash  
orchestrate toolkits import \
    --kind mcp \
    --name "mcp-toolkit" \
    --description "mcp server for watsonx retrival service" \
    --package "ibm-watsonxdata-dl-retrieval-mcp-server" \
    --command "uv run ibm-watsonxdata-dl-retrieval-mcp-server --port <port> --transport stdio" \
    --language python \
    --tools "*" \
    --app-id <app id>
```

### Transport: SSE
1. Install mcp-proxy 
```bash   
pip install mcp-proxy  
``` 
2. Run ibm-watsonxdata-dl-retrieval-mcp-server in sse transport.
 
Once prerequisites are met, the tools can be added as toolkit in WXO.
 
Example : 
```bash  
orchestrate toolkits import \ 
  --kind mcp \ 
  --name mcp_toolkit \ 
  --description "MCP server (hosted, SSE)" \ 
  --package "mcp-proxy" \ 
  --language python \ 
  --command "uvx mcp-proxy https://<mcp server endpoint>/sse" \ 
  --tools "*" 
``` 
NOTE:  
When running wxo in SAAS and MCP server locally, expose the mcp server endpoint if required.

Refer wxo documentation for more details: https://www.ibm.com/docs/en/watsonx/watson-orchestrate/base?topic=tools-importing-from-mcp-server

---

## Integrating with other Agentic Frameworks
For more examples on using Watsonx.data Document Library Retrieval MCP Server with agentic framework refer `examples`

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