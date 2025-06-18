import pytest
from unittest.mock import MagicMock, patch
import os
import requests
import json

from src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api import watsonx_data_query_handler


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
    "WATSONX_DATA_RETRIEVAL_ENDPOINT": "https://example.com/api",
    "WATSONX_DATA_API_KEY": "sampleapikey",
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://example.com/token",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_saas_access_token')
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.requests.post')
def test_watsonx_data_query_handler_valid_input_saas(mock_post, mock_get_access_token):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_data = {
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
    }
    mock_response.json.return_value = mock_data
    mock_post.return_value = mock_response
    mock_get_access_token.return_value = "mock_access_token"
    query = "how many invoices are there"
    dl_id = "12345-2524-41da-98f9-80758"
    dl_type = "project"
    container_id = "8e2cb-4256-42cc-8bbd-812e"
    result = watsonx_data_query_handler(query, dl_id, dl_type, container_id)
    assert result == 'There is a total of 50 invoices.'
    mock_post.assert_called_once()


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
    "CPD_ENDPOINT": "https://example.com/api",
    "CPD_USERNAME": "sampleapikey",
    "PD_PASSWORD": "password",
    "CA_BUNDLE_PATH": "path/to/certificate.crt"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_cpd_access_token')
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.requests.post')
def test_watsonx_data_query_handler_valid_input_cpd(mock_post, mock_get_access_token):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_data = {
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
    }
    mock_response.json.return_value = mock_data
    mock_post.return_value = mock_response
    mock_get_access_token.return_value = "mock_access_token"
    query = "how many invoices are there"
    dl_id = "12345-2524-41da-98f9-80758"
    dl_type = "project"
    container_id = "8e2cb-4256-42cc-8bbd-812e"
    result = watsonx_data_query_handler(query, dl_id, dl_type, container_id)
    assert result == 'There is a total of 50 invoices.'
    mock_post.assert_called_once()


def test_watsonx_data_query_handler_missing_query():
    with pytest.raises(ValueError) as excinfo:
        watsonx_data_query_handler(
            "", "test_library_id", "test_container_type", "test_container_id")
    assert str(excinfo.value) == "Query must be a non-empty string"


def test_watsonx_data_query_handler_missing_document_library_id():
    with pytest.raises(ValueError) as excinfo:
        watsonx_data_query_handler(
            "test query", "", "test_container_type", "test_container_id")
    assert str(excinfo.value) == "document_library_id must be a non-empty string"


def test_watsonx_data_query_handler_missing_lh_context():
    with patch('os.getenv', return_value=None) as mock_env:
        with pytest.raises(ValueError) as excinfo:
            watsonx_data_query_handler(
                "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(excinfo.value) == "LH_CONTEXT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_saas_access_token')
def test_watsonx_data_query_handler_missing_watsonx_data_retrieval_endpoint(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        watsonx_data_query_handler(
            "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(excinfo.value) == "Failed to get access token: WATSONX_DATA_RETRIEVAL_ENDPOINT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_cpd_access_token')
def test_watsonx_data_query_handler_missing_cpd_endpoint(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        watsonx_data_query_handler(
            "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(
        excinfo.value) == "Failed to get access token: CPD_ENDPOINT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
    "CPD_ENDPOINT": "https://example.com",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_cpd_access_token')
def test_watsonx_data_query_handler_missing_cpd_cabundle(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        watsonx_data_query_handler(
            "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(
        excinfo.value) == "Failed to get access token: CA_BUNDLE_PATH environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
    "WATSONX_DATA_RETRIEVAL_ENDPOINT": "https://example.com/api",
    "WATSONX_DATA_API_KEY": "sampleapikey",
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://example.com/token",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_saas_access_token')
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.requests.post')
def test_watsonx_data_query_handler_invalid_response_format(mock_post, mock_get_access_token):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid_key": "value"}
    mock_post.return_value = mock_response
    mock_get_access_token.return_value = "mock_access_token"
    with patch('requests.post', return_value=mock_response) as mock_post:
        with pytest.raises(KeyError) as excinfo:
            watsonx_data_query_handler(
                "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(
        excinfo.value) == "\"Invalid response format: 'generated_text' field missing\""


@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.retrival_service_api.get_watsonx_data_saas_access_token')
@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
    "WATSONX_DATA_RETRIEVAL_ENDPOINT": "https://example.com/api",
    "WATSONX_DATA_API_KEY": "sampleapikey",
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://example.com/token",
})
def test_watsonx_data_query_handler_timeout(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with patch('requests.post', side_effect=requests.exceptions.Timeout("Mocked timeout")) as mock_post:
        with pytest.raises(TimeoutError) as excinfo:
            watsonx_data_query_handler(
                "test query", "test_library_id", "test_container_type", "test_container_id")
    assert str(excinfo.value) == "Request to WatsonX Data API timed out after 120 seconds: https://example.com/api/api/v1/retrieval/search"
