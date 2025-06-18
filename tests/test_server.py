"""Tests for the server module of the IBM watsonx.data retrival MCP server."""

import json
import pytest
import os
from unittest.mock import patch
from src.ibm_watsonxdata_dl_retrieval_mcp_server.server import app

class TestMCPTool:
    """Tests for the Tools handler."""

    @pytest.mark.asyncio
    @patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.server.get_document_library_list')
    async def test_mcp_list_tools(self, mock_get_document_library_list):
        """Test the list tool function."""
        mock_get_document_library_list.return_value = [{'document_library_name': 'invoice_document_library', 'document_library_description': 'The document library for invoices', 'document_library_id': '12345-2524-41da-98f9-80758', 'container_type': 'project', 'container_id': '8e2cb-4256-42cc-8bbd-812e'}, {
            'document_library_name': 'insurance_document_library', 'document_library_description': 'The document library for insurance', 'document_library_id': '9e05-1d29-444f-b619-ed03', 'container_type': 'project', 'container_id': '000f-3b86-4467-8a0e-ef19'}]
        # Call the function
        result = await app._mcp_list_tools()

        # Check that the result is correct
        assert len(result) == 2
        for document_libarary in result:
            if (document_libarary.name == 'invoice_document_library12345_2524_41da_98f9_80758'):
                assert document_libarary.description == 'The document library for invoices'
            else:
                assert document_libarary.name == 'insurance_document_library9e05_1d29_444f_b619_ed03'
                assert document_libarary.description == 'The document library for insurance'
        mock_get_document_library_list.assert_called_once()

    @pytest.mark.asyncio
    @patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.server.watsonx_data_query_handler')
    @patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.server.get_document_library_list')
    async def test_mcp_call_tool(self, mock_get_document_library_list, mock_watsonx_data_query_handler):
        """Test the call tool function."""
        mock_get_document_library_list.return_value = [{'document_library_name': 'invoice_document_library', 'document_library_description': 'The document library for invoices', 'document_library_id': '12345-2524-41da-98f9-80758', 'container_type': 'project', 'container_id': '8e2cb-4256-42cc-8bbd-812e'}, {
            'document_library_name': 'insurance_document_library', 'document_library_description': 'The document library for insurance', 'document_library_id': '9e05-1d29-444f-b619-ed03', 'container_type': 'project', 'container_id': '000f-3b86-4467-8a0e-ef19'}]
        mock_watsonx_data_query_handler.return_value = json.dumps({
            "request_id": "ab2b-509e-4cb2-ba30-0a45",
            "results": [
                {
                    "source": "sql",
                    "data": [
                        {
                            "_col0": 50
                        }
                    ],
                    "metadata": {
                        "execution_time": 71,
                        "row_count": 1,
                        "sql": "SELECT COUNT(*) FROM invoices_table"
                    },
                    "summary": ""
                },
                {
                    "source": "vector",
                    "data": [
                        {
                            "dimension": "1024",
                            "distance": "0.016393",
                            "document_id": "12345-2524-41da-98f9-80758",
                            "document_name": "test_invoice.pdf",
                            "text": "This is a sample test invoice"
                        }
                    ],
                    "metadata": {
                        "execution_time": 70
                    },
                    "summary": ""
                }
            ],
            "suggested_template": {},
            "status": "success",
            "execution_time": 150,
            "generated_text": "There is a total of 50 invoices."
        })

        args = {'query': 'How many invoices are there'}
        result = await app._mcp_call_tool('invoice_document_library12345_2524_41da_98f9_80758', args)
        # Check that the result is correct
        assert len(result) == 1
        data = json.loads(result[0].text)
        assert data['generated_text'] == 'There is a total of 50 invoices.'

        mock_watsonx_data_query_handler.assert_called_once_with(
            'How many invoices are there',
            '12345-2524-41da-98f9-80758',
            'project',
            '8e2cb-4256-42cc-8bbd-812e'
        )
