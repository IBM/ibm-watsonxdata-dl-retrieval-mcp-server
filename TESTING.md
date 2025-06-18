# ibm_watsonxdata_dl_retrieval_mcp_server Tests

This directory contains tests for the ibm_watsonxdata_dl_retrieval_mcp_server.


## Running Tests

To run the tests, you can use the following command from the root of the repository:

```bash
pytest tests/
```

To run a specific test file:

```bash
pytest tests/test_server.py
```

To run a specific test:

```bash
pytest tests/test_server.py::TestMCPTool::test_mcp_list_tools
```
