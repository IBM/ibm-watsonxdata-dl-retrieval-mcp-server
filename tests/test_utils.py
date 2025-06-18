import os
import pytest
from unittest.mock import patch, MagicMock
import requests
import json

from src.ibm_watsonxdata_dl_retrieval_mcp_server.utils import get_watsonx_data_cpd_access_token
from src.ibm_watsonxdata_dl_retrieval_mcp_server.utils import get_watsonx_data_saas_access_token

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_cpd_access_token_success(mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test_token"}
        mock_post.return_value = mock_response

        access_token = get_watsonx_data_cpd_access_token()
        assert access_token == "test_token"
        mock_post.assert_called_once_with(
            url="https://test_endpoint/icp4d-api/v1/authorize",
            headers={"Content-Type": "application/json"},
            data=b'{"username": "test_user", "password": "test_password"}',
            timeout=30,
            verify="/path/to/ca_bundle"
        )

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_cpd_access_token_invalid_api_key(mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        with pytest.raises(requests.RequestException) as exc_info:
            get_watsonx_data_cpd_access_token()
        assert "Invalid API key or authentication failed" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_cpd_access_token_iam_endpoint_not_found(mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_post.return_value = mock_response

        with pytest.raises(requests.RequestException) as exc_info:
            get_watsonx_data_cpd_access_token()
        assert "IAM token service endpoint not found" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_cpd_access_token_invalid_response(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid_key": "value"}
    mock_post.return_value = mock_response
    with pytest.raises(KeyError) as exc_info:
       get_watsonx_data_cpd_access_token()
    assert "Invalid response format: \'access_token\' field missing" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_cpd_access_token_invalid_token_type(mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": 123}
        mock_post.return_value = mock_response

        with pytest.raises(KeyError) as exc_info:
            get_watsonx_data_cpd_access_token()
        assert "Invalid response format: 'token' is not a string" in str(exc_info.value)

@patch.dict(os.environ, {
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
def test_get_watsonx_data_cpd_access_token_missing_env_vars():
    with pytest.raises(ValueError) as exc_info:
        get_watsonx_data_cpd_access_token()
    print(exc_info.value)
    assert "CPD_USERNAME environment variable is not set" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
})
def test_get_watsonx_data_cpd_access_token_missing_ca_bundle():
    with pytest.raises(ValueError) as exc_info:
        get_watsonx_data_cpd_access_token()
    assert "CA_BUNDLE_PATH environment variable is not set" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
def test_get_watsonx_data_cpd_access_token_missing_cpd_password():
    with pytest.raises(ValueError) as exc_info:
        get_watsonx_data_cpd_access_token()
    assert "CPD_PASSWORD environment variable is not set" in str(exc_info.value)

@patch.dict(os.environ, {
    "CPD_USERNAME": "test_user",
    "CPD_PASSWORD": "test_password",
    "CPD_ENDPOINT": "https://test_endpoint",
    "CA_BUNDLE_PATH": "/path/to/ca_bundle"
})
def test_get_watsonx_data_cpd_access_token_timeout():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.Timeout(f"Request timed out after 30 seconds")

        with pytest.raises(TimeoutError) as exc_info:
            get_watsonx_data_cpd_access_token()
        assert "Request to IAM service timed out after 30 seconds" in str(exc_info.value)


@patch.dict(os.environ, {
    "WATSONX_DATA_API_KEY": "testapikey",
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://test_endpoint"
})
@patch('src.ibm_watsonxdata_dl_retrieval_mcp_server.utils.requests.post')
def test_get_watsonx_data_saas_access_token_success(mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        access_token = get_watsonx_data_saas_access_token()
        assert access_token == "test_token"
        mock_post.assert_called_once_with(
            url="https://test_endpoint/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": "testapikey"},
            timeout=30,
            verify=True
        )

@patch.dict(os.environ, {
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://test_endpoint"
})
def test_get_watsonx_data_saas_missing_api_key():
    with pytest.raises(ValueError) as exc_info:
        get_watsonx_data_saas_access_token()
    assert "WATSONX_DATA_API_KEY environment variable is not set" in str(exc_info.value)

@patch.dict(os.environ, {
    "WATSONX_DATA_API_KEY": "testapikey"
})
def test_get_watsonx_data_saas_missing_token_endpoint():
    with pytest.raises(ValueError) as exc_info:
        get_watsonx_data_saas_access_token()
    assert "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT environment variable is not set" in str(exc_info.value)


@patch.dict(os.environ, {
    "WATSONX_DATA_API_KEY": "testapikey",
    "WATSONX_DATA_TOKEN_GENERATION_ENDPOINT": "https://test_endpoint"
}) 
def test_get_watsonx_data_saas_access_token_timeout():
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.Timeout(f"Request timed out after 30 seconds")

        with pytest.raises(TimeoutError) as exc_info:
            get_watsonx_data_saas_access_token()
        assert "Request to IAM service timed out after 30 seconds" in str(exc_info.value)