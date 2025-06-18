import requests
import json
from typing import Dict, Any
import os
    
def get_watsonx_data_cpd_access_token() -> str:
    """
    Get an IBM IAM access token using the provided API key for CPD.

    This function authenticates with IBM Identity and Access Management (IAM)
    service to obtain a temporary access token that can be used for subsequent API
    calls to WatsonX Data services.

    Args:
        None

    Returns:
        str: A valid IAM access token that can be used in Authorization headers

    Raises:
        ValueError: If the apikey is empty or invalid
        requests.RequestException: If the IAM authentication request fails
        KeyError: If the response format from IAM service is invalid
        TimeoutError: If the request times out
    """
    user = os.getenv("CPD_USERNAME")
    password = os.getenv("CPD_PASSWORD")
    token_endpoint = os.getenv("CPD_ENDPOINT")
    cabundle = os.getenv("CA_BUNDLE_PATH")
    if not cabundle:
        raise ValueError("CA_BUNDLE_PATH environment variable is not set")
    if not user:
            raise ValueError("CPD_USERNAME environment variable is not set")
    if not password:
            raise ValueError("CPD_PASSWORD environment variable is not set")
    if not token_endpoint:
        raise ValueError("CPD_ENDPOINT environment variable is not set")


    token_url = token_endpoint + '/icp4d-api/v1/authorize'
    timeout_seconds = 30
    
    data: Dict[str, str] = {
        "username": user,
        "password": password
    }
    data_to_send = json.dumps(data).encode("utf-8")
    headers: Dict[str, str] = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.post(
            url=token_url,
            headers=headers,
            data=data_to_send,
            timeout=timeout_seconds,
            verify=cabundle,
        )
        
        if response.status_code == 401:
            raise requests.RequestException("Invalid API key or authentication failed")
        elif response.status_code == 404:
            raise requests.RequestException("IAM token service endpoint not found")
        elif response.status_code != 200:
            raise requests.RequestException(
                f"IAM token request failed with status code {response.status_code}: {response.text}"
            )
        
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise KeyError(f"Invalid JSON response from IAM service: {str(e)}")
        
        if 'token' not in response_data:
            raise KeyError("Invalid response format: 'access_token' field missing")
        
        access_token = response_data['token']
        if not isinstance(access_token, str):
            raise KeyError("Invalid response format: 'token' is not a string")
        
        return access_token
        
    except requests.Timeout:
        raise TimeoutError(f"Request to IAM service timed out after {timeout_seconds} seconds")
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to connect to IAM service: {str(e)}")
    except (KeyError, ValueError) as e:
        raise e
    except Exception as e:
        raise requests.RequestException(f"Unexpected error during IAM token request: {str(e)}")
    

def get_watsonx_data_saas_access_token() -> str:
    """
    Get an IBM cloud IAM access token using the provided API key.

    This function authenticates with IBM cloud Identity and Access Management (IAM)
    service to obtain a temporary access token that can be used for subsequent API
    calls to WatsonX Data services.

    Args:
        None

    Returns:
        str: A valid IAM access token that can be used in Authorization headers

    Raises:
        ValueError: If the apikey is empty or invalid
        requests.RequestException: If the IAM authentication request fails
        KeyError: If the response format from IAM service is invalid
        TimeoutError: If the request times out
    """
    apikey = os.getenv("WATSONX_DATA_API_KEY")
    if not apikey:
            raise ValueError("WATSONX_DATA_API_KEY environment variable is not set")

    token_endpoint = os.getenv("WATSONX_DATA_TOKEN_GENERATION_ENDPOINT")

    if not token_endpoint:
        raise ValueError("WATSONX_DATA_TOKEN_GENERATION_ENDPOINT environment variable is not set")

    token_url = token_endpoint + '/identity/token'
    timeout_seconds = 30
    
    data: Dict[str, str] = {
        'grant_type': 'urn:ibm:params:oauth:grant-type:apikey',
        'apikey': apikey
    }
    
    headers: Dict[str, str] = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    try:
        response = requests.post(
            url=token_url,
            headers=headers,
            data=data,
            timeout=timeout_seconds,
            verify=True
        )
        
        if response.status_code == 401:
            raise requests.RequestException("Invalid API key or authentication failed")
        elif response.status_code == 404:
            raise requests.RequestException("IAM token service endpoint not found")
        elif response.status_code != 200:
            raise requests.RequestException(
                f"IAM token request failed with status code {response.status_code}: {response.text}"
            )
        
        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            raise KeyError(f"Invalid JSON response from IAM service: {str(e)}")
        
        if 'access_token' not in response_data:
            raise KeyError("Invalid response format: 'access_token' field missing")
        
        access_token = response_data['access_token']
        if not isinstance(access_token, str):
            raise KeyError("Invalid response format: 'access_token' is not a string")
        
        return access_token
        
    except requests.Timeout:
        raise TimeoutError(f"Request to IAM service timed out after {timeout_seconds} seconds")
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to connect to IAM service: {str(e)}")
    except (KeyError, ValueError) as e:
        raise e
    except Exception as e:
        raise requests.RequestException(f"Unexpected error during IAM token request: {str(e)}")
    