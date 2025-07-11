import pytest
import requests


@pytest.fixture(scope="session")
def base_url():
    """
    Fixture to provide the base URL for the API.
    Scoped to 'session' so it's created once for all tests.
    """
    return "http://localhost:9000"

@pytest.fixture(scope="session")
def api_client(base_url):
    """
    Fixture to provide a requests.Session() object.
    This is good for maintaining persistent headers (like authentication tokens)
    and connection pooling across multiple requests.
    Scoped to 'session'.
    """
    session = requests.Session()
    # Example: Add common headers if needed
    session.headers.update({"Accept": "application/json"})
    # Example: Add authentication (e.g., Bearer token)
    # session.headers.update({"Authorization": "Bearer your_auth_token"})
    yield session  # Provide the session object to tests
    session.close() # Close the session after all tests are done (optional but good practice)

def test_post_incomplete_timeseries_document(api_client, base_url):
    """
    Test that ensure that an incomplete timeseries document is not accepted.
    """

    #missing currentGeozone": "Downtown",  "hasDriver": true, "isOilLeak": false,  "isEngineRunning": true,  "isCrashed": false,  "currentRoute": 50
    data_string = """
    {  
        "vehicle": {
            "carID": "12345"
        },
        "gasLevel": 60,  
        "maxGasLevel": 100,  
        "oilTemperature": 95,  
        "oilLevel": 80,  
        "distanceTraveled": 1200,  
        "performanceScore": 85,  
        "avaliabilityScore": 90,  
        "runTime": 3600,  
        "qualityScore": 95  
    }  
    """
    expected_missing_field_names = [
        "currentGeozone",
        "hasDriver",
        "isOilLeak",
        "isEngineRunning",
        "isCrashed",
        "currentRoute"
    ]

    # Manually specify headers
    headers = {"Content-Type": "application/json"}

    # Use data=, but also pass the headers=
    response = api_client.post(
        f"{base_url}/timeseries", 
        data=data_string, 
        headers=headers
    )

    # Assert the status code first
    assert response.status_code == 422 # Unprocessable Entity

    response_body = response.json()

    # Assert the structure of the response body
    assert "detail" in response_body
    assert isinstance(response_body["detail"], list)
    assert len(response_body["detail"]) > 0

    # Extract the actual missing field names from the response
    actual_missing_field_names = [
    error["loc"][-1]
    for error in response_body["detail"]
    if error.get("type") == "missing" 
    ]

    # Assert that all expected missing field names are in the actual missing field names
    for field_name in expected_missing_field_names:
        assert field_name in actual_missing_field_names, f"Expected missing field '{field_name}' not found in response."
    # Assert that the number of missing fields matches
    assert len(actual_missing_field_names) == len(expected_missing_field_names), \
        f"Expected {len(expected_missing_field_names)} missing fields, but got {len(actual_missing_field_names)}."
    

def test_post_empty_timeseries_document(api_client, base_url):
    """
    Test that ensure that an empty timeseries document is not accepted.
    """
    data_string = "{}"

    # Manually specify headers
    headers = {"Content-Type": "application/json"}

    # Use data=, but also pass the headers=
    response = api_client.post(
        f"{base_url}/timeseries", 
        data=data_string, 
        headers=headers
    )

    # Assert the status code first
    assert response.status_code == 422 # Unprocessable Entity

    response_body = response.json()

    # Assert the structure of the response body
    assert "detail" in response_body
    assert isinstance(response_body["detail"], list)
    assert len(response_body["detail"]) > 0

    # Assert that the error message indicates missing fields
    missing_fields = [error for error in response_body["detail"] if error.get("type") == "missing"]
    assert len(missing_fields) > 0, "Expected missing fields in the error details."

def test_post_invalid_json(api_client, base_url):
    """
    Test that ensure that an invalid JSON document is not accepted.
    """
    data_string = "{invalid_json: true"  # Missing closing brace

    # Manually specify headers
    headers = {"Content-Type": "application/json"}

    # Use data=, but also pass the headers=
    response = api_client.post(
        f"{base_url}/timeseries", 
        data=data_string, 
        headers=headers
    )

    # Assert the status code first
    assert response.status_code == 422 # Unprocessable Entity

    response_body = response.json()

    # Assert the structure of the response body
    assert "detail" in response_body
    assert isinstance(response_body["detail"], list)
    assert len(response_body["detail"]) > 0

    # Assert that the error message indicates invalid JSON
    assert any("value is not a valid dict" in str(error.get("msg", "")) for error in response_body["detail"]), \
        "Expected error message indicating invalid JSON."

def test_post_non_json_content_type(api_client, base_url):
    """
    Test that ensure that a non-JSON content type is not accepted.
    """
    data_string = "<xml><data>invalid</data></xml>"

    # Manually specify headers
    headers = {"Content-Type": "application/xml"}

    # Use data=, but also pass the headers=
    response = api_client.post(
        f"{base_url}/timeseries", 
        data=data_string, 
        headers=headers
    )

    # Assert the status code first
    assert response.status_code == 422 # Unprocessable Entity

    response_body = response.json()

    # Assert the structure of the response body
    assert "detail" in response_body
    assert isinstance(response_body["detail"], list)
    assert len(response_body["detail"]) > 0

    # Assert that the error message indicates unsupported media type or invalid JSON
    assert any("value is not a valid dict" in str(error.get("msg", "")) for error in response_body["detail"]), \
        "Expected error message indicating unsupported media type or invalid JSON." 