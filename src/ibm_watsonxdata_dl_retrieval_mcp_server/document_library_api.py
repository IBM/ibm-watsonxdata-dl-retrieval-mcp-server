import requests
import json
import os
from .utils import get_watsonx_data_saas_access_token
from .utils import get_watsonx_data_cpd_access_token

def get_document_library_list():
    """
    This function makes a call to the Data Library API to retrieve a list of document libraries.

    It checks for required environment variables, constructs the API request, and processes the response.
    The function returns a list of dictionaries, each containing details about a document library.

    Parameters:
    None

    Returns:
    list: A list of dictionaries, each containing details about a document library.

    Raises:
    ValueError: If required environment variables or parameters are missing.
    requests.RequestException: If the API request fails.
    KeyError: If the response format is invalid or expected keys are missing.
    TimeoutError: If the request times out.
    """
    context = os.getenv("LH_CONTEXT")
    if not context:
        raise ValueError("LH_CONTEXT environment variable is not set")
    
    if context in ('saas', 'SAAS'):
        dl_endpoint = os.getenv("DOCUMENT_LIBRARY_API_ENDPOINT")

        if not dl_endpoint:
            raise ValueError("DOCUMENT_LIBRARY_API_ENDPOINT environment variable is not set")

        try:
            access_token = get_watsonx_data_saas_access_token()
        except Exception as e:
            raise ValueError(f"Failed to get access token: {str(e)}") from e
    else:
        dl_endpoint = os.getenv("CPD_ENDPOINT")

        if not dl_endpoint:
            raise ValueError("CPD_ENDPOINT environment variable is not set")
        
        cabundle = os.getenv("CA_BUNDLE_PATH")
        if not cabundle:
            raise ValueError("CA_BUNDLE_PATH environment variable is not set")
        try:
            access_token = get_watsonx_data_cpd_access_token()
        except Exception as e:
            raise ValueError(f"Failed to get access token: {str(e)}") from e

    
    url = dl_endpoint + '/v3/search?role=viewer&auth_cache=false&auth_scope=any'

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    data = {
        "_source": [
        "metadata.name",
        "metadata.description",
        "artifact_id",
        "entity.assets.project_id",
        "entity.assets.catalog_id",
        "entity.assets.space_id"
        ],
        "query": {
            "bool" : {
                "filter": [
                    { "term": { "metadata.artifact_type": "ibm_document_library" }}
                ]
            }
        } 
    }
    
    try:
        if context in ('cpd', 'CPD'):
            response = requests.post(url, headers=headers, json=data, timeout=120, verify=cabundle)
        elif context in ('saas', 'SAAS'):
            response = requests.post(url, headers=headers, json=data, timeout=120, verify=True)
        else:
            raise ValueError("Please give either `CPD` or `SAAS` as value for LH_CONTEXT environment variable")
        
        if response.status_code == 401:
            raise requests.RequestException(f"Authentication failed (Status 401). Check API key/token. Response: {response.text}")
        elif response.status_code == 404:
            raise requests.RequestException(f"Invalid API endpoint (Status 404): {dl_endpoint}")
        elif response.status_code != 200:
            raise requests.RequestException(
                f"API request failed with status code {response.status_code}: {response.text}"
            )

        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
             raise KeyError(f"Invalid JSON response received: {str(e)}") from e
        
        input_array = response_data["rows"]
        
        output_array = []
        for item in input_array:
            transformed = {
                "document_library_name": item.get("metadata", {}).get("name", ""),
                "document_library_description": item.get("metadata", {}).get("description", "").strip(),
                "document_library_id": item.get("artifact_id", "")
            }
            project_id = item.get("entity", {}).get("assets", {}).get("project_id")
            if project_id:
                transformed["container_type"] = "project"
                transformed["container_id"] = project_id
            catalog_id = item.get("entity", {}).get("assets", {}).get("catalog_id")
            if catalog_id:
                transformed["container_type"] = "catalog"
                transformed["container_id"] = catalog_id
            space_id = item.get("entity", {}).get("assets", {}).get("space_id")
            if space_id:
                transformed["container_type"] = "space"
                transformed["container_id"] = space_id

            output_array.append(transformed)
        return (output_array)
    except requests.Timeout:
        raise TimeoutError(f"Request to list Data Library API timed out after 120 seconds")
    except requests.RequestException as e:
        raise requests.RequestException(f"API request communication failed: {str(e)}") from e
    except (KeyError, ValueError) as e:
        raise e
    except Exception as e:
        raise Exception(f"Unexpected error during API call: {str(e)}") from e