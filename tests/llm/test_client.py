# tests/llm/test_client.py
import pytest
import httpx
from dialogllm.llm.client import OllamaClient


class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise httpx.HTTPError(f"HTTP Error: {self.status_code}")

    def json(self):
        return self.json_data

@pytest.fixture
def mock_httpx_client(mocker):
    async def mock_post(*args, **kwargs):
        if kwargs['json']['prompt'] == "test_prompt_error":
            return MockResponse(500, {"error": "Internal Server Error"})
        if kwargs['json']['prompt'] == "test_prompt_structured":
            return MockResponse(200, {"response": '{"field1": "test value", "field2": 42, "field3": true}'})
        if kwargs['json']['prompt'] == "test_prompt_structured_invalid":
            return MockResponse(200, {"response": '{"field1": 42, "field2": "not an integer", "field3": "not a boolean"}'})
        if kwargs['json']['prompt'] == "test_prompt_structured_no_response":
            return MockResponse(200, {"other_field": '{"name": "Test Name", "value": 10}'})
        return MockResponse(200, {"response": "test response"})
    mocker.patch("httpx.AsyncClient.post", new_callable=mocker.AsyncMock, side_effect=mock_post)

@pytest.mark.asyncio
async def test_generate_success(mock_httpx_client):
    client = OllamaClient()
    response = await client.generate("test_prompt")
    assert response["response"] == "test response"

@pytest.mark.asyncio
async def test_generate_error(mock_httpx_client):
    client = OllamaClient()
    with pytest.raises(httpx.HTTPError):
        await client.generate("test_prompt_error")

@pytest.mark.asyncio
async def test_generate_structured_success(mock_httpx_client, test_model):
    client = OllamaClient()
    response = await client.generate_structured("test_prompt_structured", response_model=test_model)
    assert isinstance(response, test_model)
    assert response.field1 == "test value"
    assert response.field2 == 42
    assert response.field3 is True

@pytest.mark.asyncio
async def test_generate_structured_validation_error(mock_httpx_client, test_model):
    client = OllamaClient()
    with pytest.raises(ValueError) as excinfo:
        await client.generate_structured("test_prompt_structured_invalid", response_model=test_model)
    assert "Failed to parse LLM response to Pydantic model" in str(excinfo.value)

@pytest.mark.asyncio
async def test_generate_structured_key_error(mock_httpx_client, test_model):
    client = OllamaClient()
    with pytest.raises(ValueError) as excinfo:
        await client.generate_structured("test_prompt_structured_no_response", response_model=test_model)
    assert "LLM response missing 'response' field" in str(excinfo.value)