import requests
import json
import os
from .utils import get_watsonx_data_saas_access_token
from .utils import get_watsonx_data_cpd_access_token

def watsonx_data_query_handler(query: str, document_library_id: str, container_type: str, container_id: str) -> str:
    """Make a query to the WatsonX Data retrieval API.

    This function sends a natural language query to the WatsonX Data retrieval API
    using the specified document library ID and container details.

    Args:
        query (str): The natural language query to be processed.
        document_library_id (str): The unique identifier for the document library to query.
        container_type (str): The type of container to query.
        container_id (str): The unique identifier for the container to query.

    Returns:
        str: The generated text response from WatsonX Data.

    Raises:
        ValueError: If required parameters or environment variables are missing.
        requests.RequestException: If the API request fails.
        KeyError: If the response format is invalid or expected keys are missing.
        TimeoutError: If the request times out.
    """
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    if not document_library_id or not isinstance(document_library_id, str):
        raise ValueError("document_library_id must be a non-empty string")
    
    context = os.getenv("LH_CONTEXT")
    
    if not context:
        raise ValueError("LH_CONTEXT environment variable is not set")

    try:
        if context in ('saas', 'SAAS'):
            access_token = get_watsonx_data_saas_access_token()
            retrival_endpoint = os.getenv("WATSONX_DATA_RETRIEVAL_ENDPOINT")
            if not retrival_endpoint:
                raise ValueError("WATSONX_DATA_RETRIEVAL_ENDPOINT environment variable is not set")
        else :
            access_token = get_watsonx_data_cpd_access_token()
            retrival_endpoint = os.getenv("CPD_ENDPOINT")
            if not retrival_endpoint:
                raise ValueError("CPD_ENDPOINT environment variable is not set")
            cabundle = os.getenv("CA_BUNDLE_PATH")
            if not cabundle:
                raise ValueError("CA_BUNDLE_PATH environment variable is not set")

    except Exception as e:
        raise ValueError(f"Failed to get access token: {str(e)}") from e

    inference_url = retrival_endpoint + '/api/v1/retrieval/search'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }

    data = {
        "query": query,
        "document_library_id": document_library_id,
        "container_id": container_id,
        "container_type": container_type,                           
        "searchConfig": [                                      
            {
                "type": "sql",
                "enabled": True
            },
            {
                "type": "vector",
                "limit": 15,
                "enabled": True
            }
        ],
        "search_inference_config": {                     
            "enabled": True,
            "inference_model_id": "meta-llama/llama-3-3-70b-instruct"
        },
        "provide_suggested_template": False 
    }

    try:
        if context in ('saas', 'SAAS'):
            response = requests.post(inference_url, headers=headers, json=data, timeout=120, verify=True)
        elif context in ('cpd', 'CPD'):
            response = requests.post(inference_url, headers=headers, json=data, timeout=120, verify=cabundle)
        else:
            raise ValueError("Please give either `CPD` or `SAAS` as value for LH_CONTEXT environment variable")

        if response.status_code == 401:
            raise requests.RequestException(f"Authentication failed (Status 401). Check API key/token. Response: {response.text}")
        elif response.status_code == 404:
            raise requests.RequestException(f"Invalid API endpoint (Status 404): {inference_url}")
        elif response.status_code != 200:
            raise requests.RequestException(
                f"API request failed with status code {response.status_code}: {response.text}"
            )

        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
             raise KeyError(f"Invalid JSON response received: {str(e)}") from e

        if 'generated_text' not in response_data:
            print(f"DEBUG: API Response Data: {response_data}")
            raise KeyError("Invalid response format: 'generated_text' field missing")

        generated_text = response_data['generated_text']
        if not isinstance(generated_text, str):
            raise KeyError("Invalid response format: 'generated_text' is not a string")

        return generated_text

    except requests.Timeout:
        raise TimeoutError(f"Request to WatsonX Data API timed out after 120 seconds: {inference_url}")
    except requests.RequestException as e:
        raise requests.RequestException(f"API request communication failed: {str(e)}") from e
    except (KeyError, ValueError) as e:
        raise e
    except Exception as e:
        raise Exception(f"Unexpected error during API call: {str(e)}") from e