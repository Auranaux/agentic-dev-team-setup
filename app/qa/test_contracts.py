import pytest
import yaml
import json
from fastapi.testclient import TestClient
from app.main import app
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

client = TestClient(app)

def test_contracts_yaml_is_valid():
    """Test that contracts/api.yaml is a valid OpenAPI spec"""
    try:
        spec_dict, spec_url = read_from_filename("contracts/api.yaml")
        validate_spec(spec_dict)
    except FileNotFoundError:
        pytest.skip("contracts/api.yaml not found")
    except Exception as e:
        pytest.fail(f"Invalid OpenAPI spec: {e}")

def test_served_openapi_matches_contract():
    """Test that served /openapi.json matches contracts/api.yaml"""
    try:
        with open("contracts/api.yaml", 'r') as f:
            contract = yaml.safe_load(f)
        
        response = client.get("/openapi.json")
        assert response.status_code == 200
        served_spec = response.json()
        
        contract_paths = contract.get("paths", {})
        served_paths = served_spec.get("paths", {})
        
        for path, methods in contract_paths.items():
            assert path in served_paths, f"Path {path} missing from served spec"
            
            for method, spec in methods.items():
                assert method in served_paths[path], f"Method {method} missing for path {path}"
                
                contract_responses = spec.get("responses", {})
                served_responses = served_paths[path][method].get("responses", {})
                
                for response_code in contract_responses.keys():
                    assert response_code in served_responses, \
                        f"Response code {response_code} missing for {method} {path}"
    
    except FileNotFoundError:
        pytest.skip("contracts/api.yaml not found")

def test_drafts_endpoints_in_contract():
    """Test that drafts endpoints are properly defined in contract"""
    try:
        with open("contracts/api.yaml", 'r') as f:
            contract = yaml.safe_load(f)
        
        paths = contract.get("paths", {})
        
        assert "/v1/drafts" in paths
        assert "/v1/drafts/{id}" in paths
        
        drafts_path = paths["/v1/drafts"]
        assert "get" in drafts_path
        assert "post" in drafts_path
        
        drafts_id_path = paths["/v1/drafts/{id}"]
        assert "get" in drafts_id_path
        assert "put" in drafts_id_path
        assert "delete" in drafts_id_path
        
    except FileNotFoundError:
        pytest.skip("contracts/api.yaml not found")

def test_openapi_json_endpoint():
    """Test that /openapi.json endpoint works"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

def test_docs_endpoint():
    """Test that /docs endpoint works"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
