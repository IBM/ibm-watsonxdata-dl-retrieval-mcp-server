import os
import pytest
from unittest.mock import MagicMock, patch
import requests
from src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api import get_document_library_list


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
    "DOCUMENT_LIBRARY_API_ENDPOINT": "https://example.com",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_saas_access_token')
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.requests.post')
def test_get_document_library_list_saas(mock_post, mock_get_access_token):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_data = {
        "size": 1,
        "rows": [
            {
                "metadata": {
                    "name": "sample_document_library",
                    "artifact_type": "ibm_document_library",
                    "modified_on": "2025-06-17T06:42:25Z",
                    "tags": [],
                    "description": "This is sample document libraray"
                },
                "entity": {
                    "assets": {
                        "project_id": "123456",
                        "resource_key": "123456",
                        "source_system_history": {
                            "asset_ids": [],
                            "system_ids": []
                        },
                        "rov": {
                            "privacy": "public",
                            "owners": [
                                "sample-owner"
                            ],
                            "viewers": [],
                            "editors": []
                        }
                    }
                },
                "artifact_id": "1234-5678",
                "provider_type_id": "cams"
            }]
    }

    mock_response.json.return_value = mock_data
    mock_post.return_value = mock_response
    mock_get_access_token.return_value = "mock_access_token"
    result = get_document_library_list()
    data = result[0]
    assert data["document_library_name"] == "sample_document_library"
    assert data["document_library_description"] == "This is sample document libraray"
    assert data["document_library_id"] == "1234-5678"
    assert data["container_type"] == "project"
    assert data["container_id"] == "123456"


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
    "CPD_ENDPOINT": "https://example.com",
    "CA_BUNDLE_PATH": "path/to/ca_bundle.crt"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_cpd_access_token')
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.requests.post')
def test_get_document_library_list_cpd(mock_post, mock_get_access_token):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_data = {
        "size": 1,
        "rows": [
            {
                "metadata": {
                    "name": "sample_document_library",
                    "artifact_type": "ibm_document_library",
                    "modified_on": "2025-06-17T06:42:25Z",
                    "tags": [],
                    "description": "This is sample document libraray"
                },
                "entity": {
                    "assets": {
                        "project_id": "123456",
                        "resource_key": "123456",
                        "source_system_history": {
                            "asset_ids": [],
                            "system_ids": []
                        },
                        "rov": {
                            "privacy": "public",
                            "owners": [
                                "sample-owner"
                            ],
                            "viewers": [],
                            "editors": []
                        }
                    }
                },
                "artifact_id": "1234-5678",
                "provider_type_id": "cams"
            }]
    }

    mock_response.json.return_value = mock_data
    mock_post.return_value = mock_response
    mock_get_access_token.return_value = "mock_access_token"
    result = get_document_library_list()
    data = result[0]
    assert data["document_library_name"] == "sample_document_library"
    assert data["document_library_description"] == "This is sample document libraray"
    assert data["document_library_id"] == "1234-5678"
    assert data["container_type"] == "project"
    assert data["container_id"] == "123456"


def test_get_document_library_list_missing_lh_context():
    with patch('os.getenv', return_value=None) as mock_env:
        with pytest.raises(ValueError) as excinfo:
            get_document_library_list()
    assert str(excinfo.value) == "LH_CONTEXT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_saas_access_token')
def test_get_document_library_list_missing_watsonx_data_retrieval_endpoint(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        get_document_library_list()
    assert str(
        excinfo.value) == "DOCUMENT_LIBRARY_API_ENDPOINT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_saas_access_token')
def test_get_document_library_list_missing_cpd_endpoint(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        get_document_library_list()
    assert str(excinfo.value) == "CPD_ENDPOINT environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "CPD",
    "CPD_ENDPOINT": "https://example.com"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_saas_access_token')
def test_get_document_library_list_missing_cpd_cabundle(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with pytest.raises(ValueError) as excinfo:
        get_document_library_list()
    assert str(excinfo.value) == "CA_BUNDLE_PATH environment variable is not set"


@patch.dict(os.environ, {
    "LH_CONTEXT": "SAAS",
    "DOCUMENT_LIBRARY_API_ENDPOINT": "https://example.com/api",
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.document_library_api.get_watsonx_data_saas_access_token')
def test_wget_document_library_list_timeout(mock_get_access_token):
    mock_get_access_token.return_value = "mock_access_token"
    with patch('requests.post', side_effect=requests.exceptions.Timeout("Mocked timeout")) as mock_post:
        with pytest.raises(TimeoutError) as excinfo:
            get_document_library_list()
    assert str(
        excinfo.value) == "Request to list Data Library API timed out after 120 seconds"
